from flask import Flask, request, jsonify
import requests
import extruct
from w3lib.html import get_base_url
from urllib.parse import urlparse
from recommendations import analyze_schemas, SCHEMA_REQUIREMENTS

app = Flask(__name__)
app.url_map.strict_slashes = False

# Social platforms for sameAs analysis
SOCIAL_PLATFORMS = {
    'facebook.com': 'facebook',
    'fb.com': 'facebook',
    'instagram.com': 'instagram',
    'twitter.com': 'twitter',
    'x.com': 'twitter',
    'linkedin.com': 'linkedin',
    'youtube.com': 'youtube',
    'tiktok.com': 'tiktok',
    'pinterest.com': 'pinterest',
    'wikidata.org': 'wikidata',
    'wikipedia.org': 'wikipedia',
}


def validate_url(url):
    """Validate that a URL has a proper format"""
    parsed = urlparse(url)
    return parsed.scheme in ('http', 'https') and bool(parsed.netloc)


def fetch_page(url):
    """Fetch HTML content from URL"""
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
    response = requests.get(url, headers=headers, timeout=15)
    response.raise_for_status()
    return response.text


def extract_schemas(html, url):
    """Extract all structured data from HTML"""
    base_url = get_base_url(html, url)
    metadata = extruct.extract(html, base_url=base_url, syntaxes=['json-ld', 'opengraph'])
    return metadata


def get_types_list(schema):
    """Get @type as a list, always returns list"""
    schema_type = schema.get('@type', schema.get('type', []))
    if isinstance(schema_type, str):
        return [schema_type]
    return schema_type if schema_type else []


def get_primary_type(schema):
    """Get the primary (first) type from a schema"""
    types = get_types_list(schema)
    return types[0] if types else None


def flatten_graph(json_ld_list):
    """Flatten all JSON-LD blocks and @graph arrays into a single entity list"""
    entities = []

    for block_idx, block in enumerate(json_ld_list):
        if '@graph' in block:
            for entity_idx, entity in enumerate(block['@graph']):
                entity['_source'] = f'json_ld[{block_idx}].@graph'
                entity['_source_index'] = entity_idx
                entities.append(entity)
        else:
            block['_source'] = f'json_ld[{block_idx}]'
            block['_source_index'] = 0
            entities.append(block)

    return entities


def categorize_entity(types):
    """Categorize entity based on its types"""
    types_lower = [t.lower() for t in types]

    if any('organization' in t or 'business' in t for t in types_lower):
        return 'organization'
    if any('website' in t for t in types_lower):
        return 'website'
    if any('webpage' in t for t in types_lower):
        return 'webpage'
    if any('article' in t or 'posting' in t or 'news' in t for t in types_lower):
        return 'article'
    if any('product' in t for t in types_lower):
        return 'product'
    if any('person' in t for t in types_lower):
        return 'person'
    if any('image' in t for t in types_lower):
        return 'image'
    if any('video' in t for t in types_lower):
        return 'video'
    if any('event' in t for t in types_lower):
        return 'event'
    if any('faq' in t for t in types_lower):
        return 'faq'
    if any('howto' in t for t in types_lower):
        return 'howto'
    if any('breadcrumb' in t for t in types_lower):
        return 'breadcrumb'
    if any('review' in t or 'rating' in t for t in types_lower):
        return 'review'

    return 'other'


def extract_entity_data(entity):
    """Extract normalized data from an entity"""
    types = get_types_list(entity)

    return {
        'id': entity.get('@id'),
        'types': types,
        'category': categorize_entity(types),
        'name': entity.get('name'),
        'url': entity.get('url'),
        'source': entity.get('_source', 'unknown')
    }


def extract_sameAs(entity):
    """Extract and categorize sameAs links"""
    same_as = entity.get('sameAs', [])
    if isinstance(same_as, str):
        same_as = [same_as]

    result = {
        'wikidata': None,
        'wikipedia': None,
        'social': {}
    }

    for link in same_as:
        if not isinstance(link, str):
            continue

        link_lower = link.lower()
        for domain, platform in SOCIAL_PLATFORMS.items():
            if domain in link_lower:
                if platform == 'wikidata':
                    result['wikidata'] = link
                elif platform == 'wikipedia':
                    result['wikipedia'] = link
                else:
                    result['social'][platform] = link
                break

    return result


def extract_address(entity):
    """Extract normalized address from entity"""
    address = entity.get('address', {})
    if isinstance(address, str):
        return {'raw': address}
    if not isinstance(address, dict):
        return None

    return {
        'street': address.get('streetAddress'),
        'locality': address.get('addressLocality'),
        'region': address.get('addressRegion'),
        'postal_code': address.get('postalCode'),
        'country': address.get('addressCountry')
    }


def build_identity(entities, page_url):
    """Build identity section from entities"""
    identity = {
        'organization': None,
        'website': None,
        'page': None
    }

    for entity in entities:
        types = get_types_list(entity)
        category = categorize_entity(types)
        entity_id = entity.get('@id', '')

        # Find Organization
        if category == 'organization' and not identity['organization']:
            same_as_data = extract_sameAs(entity)
            identity['organization'] = {
                'id': entity_id,
                'types': types,
                'name': entity.get('name'),
                'url': entity.get('url'),
                'logo': entity.get('logo', {}).get('url') if isinstance(entity.get('logo'), dict) else entity.get('logo'),
                'telephone': entity.get('telephone'),
                'email': entity.get('email'),
                'address': extract_address(entity),
                'same_as': same_as_data,
                'description': entity.get('description')
            }

        # Find WebSite
        elif category == 'website' and not identity['website']:
            has_search = bool(entity.get('potentialAction'))
            identity['website'] = {
                'id': entity_id,
                'name': entity.get('name'),
                'url': entity.get('url'),
                'language': entity.get('inLanguage'),
                'has_search_action': has_search
            }

        # Find WebPage (matching current URL)
        elif category == 'webpage':
            entity_url = entity.get('url', '')
            # Match if URL is same as page URL or if it's the first webpage found
            if entity_url == page_url or not identity['page']:
                identity['page'] = {
                    'id': entity_id,
                    'type': get_primary_type(entity),
                    'name': entity.get('name'),
                    'description': entity.get('description'),
                    'url': entity.get('url'),
                    'language': entity.get('inLanguage'),
                    'date_published': entity.get('datePublished'),
                    'date_modified': entity.get('dateModified'),
                    'primary_image': entity.get('primaryImageOfPage', {}).get('url') if isinstance(entity.get('primaryImageOfPage'), dict) else entity.get('primaryImageOfPage')
                }

    return identity


def build_graph(entities):
    """Build entity graph with relationships"""
    graph_entities = []
    connections = []

    # Relationship fields to track
    relationship_fields = ['isPartOf', 'publisher', 'author', 'about', 'mainEntity',
                          'provider', 'organizer', 'performer', 'itemReviewed',
                          'parentOrganization', 'subOrganization', 'memberOf']

    for entity in entities:
        types = get_types_list(entity)
        if not types:
            continue

        entity_id = entity.get('@id')

        graph_entities.append({
            'id': entity_id,
            'types': types,
            'name': entity.get('name'),
            'category': categorize_entity(types)
        })

        # Extract relationships
        for rel_field in relationship_fields:
            rel_value = entity.get(rel_field)
            if rel_value:
                target_id = None
                if isinstance(rel_value, dict):
                    target_id = rel_value.get('@id')
                elif isinstance(rel_value, str) and rel_value.startswith('#'):
                    target_id = rel_value

                if target_id and entity_id:
                    connections.append({
                        'from': entity_id,
                        'relation': rel_field,
                        'to': target_id
                    })

    return {
        'entities': graph_entities,
        'connections': connections
    }


def extract_opengraph(og_data):
    """Extract normalized OpenGraph data"""
    if not og_data:
        return None

    og = og_data[0] if isinstance(og_data, list) and og_data else og_data
    if not isinstance(og, dict):
        return None

    return {
        'title': og.get('og:title'),
        'description': og.get('og:description'),
        'url': og.get('og:url'),
        'image': og.get('og:image'),
        'type': og.get('og:type'),
        'site_name': og.get('og:site_name'),
        'locale': og.get('og:locale')
    }


def check_rich_results_eligibility(entities):
    """Check which Rich Results this page is eligible for"""
    eligible = []
    potential = []

    types_found = set()
    for entity in entities:
        types_found.update(get_types_list(entity))

    for entity_type, requirements in SCHEMA_REQUIREMENTS.items():
        if entity_type in types_found:
            rich_result = requirements.get('rich_result')
            if rich_result:
                required_fields = requirements.get('required', [])
                for entity in entities:
                    if entity_type in get_types_list(entity):
                        missing = [f for f in required_fields if not entity.get(f)]
                        if not missing:
                            if rich_result not in eligible:
                                eligible.append(rich_result)
                        else:
                            if rich_result not in potential and rich_result not in eligible:
                                potential.append(rich_result)

    return {
        'eligible': eligible,
        'potential': potential
    }


@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Action-oriented schema analysis.
    Returns actionable insights focused on SEO impact.
    """
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    if not validate_url(url):
        return jsonify({'error': 'Invalid URL format. Must start with http:// or https://'}), 400

    try:
        # Fetch and extract
        html = fetch_page(url)
        schemas = extract_schemas(html, url)

        # Flatten all JSON-LD into entities
        json_ld = schemas.get('json-ld', [])
        entities = flatten_graph(json_ld)

        # Build identity
        identity = build_identity(entities, url)

        # Build graph
        graph = build_graph(entities)

        # Extract OpenGraph
        opengraph = extract_opengraph(schemas.get('opengraph'))

        # Comprehensive recommendations engine
        analysis = analyze_schemas(entities, url, opengraph)

        # Check Rich Results eligibility
        rich_results = check_rich_results_eligibility(entities)

        # Calculate health based on analysis
        severity_counts = analysis['by_severity']
        if severity_counts['critical'] > 0:
            health_status = 'broken'
        elif severity_counts['high'] > 3:
            health_status = 'needs_work'
        elif severity_counts['high'] > 0 or severity_counts['medium'] > 5:
            health_status = 'good'
        else:
            health_status = 'healthy'

        # Build response
        return jsonify({
            'url': url,

            'summary': {
                'health': health_status,
                'page_type': analysis['page_type'],
                'schemas_found': analysis['schemas_found'],
                'total_issues': analysis['total_issues'],
                'by_severity': severity_counts,
                'entities_found': len(graph['entities']),
                'json_ld_blocks': len(json_ld)
            },

            'recommendations': analysis['recommendations'],

            'identity': identity,

            'graph': graph,

            'rich_results': rich_results,

            'social': opengraph,

            'trust_signals': {
                'has_organization': identity['organization'] is not None,
                'has_wikidata': bool(identity['organization'] and identity['organization'].get('same_as', {}).get('wikidata')),
                'has_contact': bool(identity['organization'] and (identity['organization'].get('telephone') or identity['organization'].get('email'))),
                'social_profiles_count': len(identity['organization'].get('same_as', {}).get('social', {})) if identity['organization'] else 0
            }
        })

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/extract-schema', methods=['POST'])
def extract_schema():
    """Legacy endpoint - returns raw schema data"""
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    if not validate_url(url):
        return jsonify({'error': 'Invalid URL format. Must start with http:// or https://'}), 400

    try:
        html = fetch_page(url)
        base_url = get_base_url(html, url)
        metadata = extruct.extract(html, base_url=base_url)
        return jsonify(metadata)
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/extract-entities', methods=['POST'])
def extract_entities():
    """
    Extract all schema entities with full data.
    Returns a flat list of entities with their complete JSON-LD data.
    Designed for direct import into Neo4j.
    """
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({'error': 'URL is required'}), 400

    if not validate_url(url):
        return jsonify({'error': 'Invalid URL format. Must start with http:// or https://'}), 400

    try:
        html = fetch_page(url)
        schemas = extract_schemas(html, url)

        json_ld = schemas.get('json-ld', [])
        flat_entities = flatten_graph(json_ld)

        # Build structured entity list for Neo4j import
        entities = []
        for entity in flat_entities:
            types = get_types_list(entity)
            if not types:
                continue

            source_str = entity.get('_source', '')
            is_graph = '.@graph' in source_str
            block_idx = int(source_str.split('[')[1].split(']')[0]) if '[' in source_str else 0

            entities.append({
                'id': entity.get('@id'),
                'type': types,
                'category': categorize_entity(types),
                'data': entity,
                'source': {
                    'block': block_idx,
                    'location': '@graph' if is_graph else 'root',
                    'index': entity.get('_source_index', 0)
                }
            })

        # Count by type
        type_counts = {}
        for entity in entities:
            for t in entity['type']:
                type_counts[t] = type_counts.get(t, 0) + 1

        return jsonify({
            'url': url,
            'entities': entities,
            'summary': {
                'total_entities': len(entities),
                'json_ld_blocks': len(json_ld),
                'types': type_counts
            }
        })
    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3015)
