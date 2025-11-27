from flask import Flask, request, jsonify
import requests
import extruct
from w3lib.html import get_base_url
from urllib.parse import urlparse
import re

app = Flask(__name__)
app.url_map.strict_slashes = False

# Google's required fields for Rich Results eligibility
RICH_RESULTS_REQUIREMENTS = {
    'Product': {
        'required': ['name'],
        'recommended': ['image', 'description', 'offers', 'aggregateRating', 'review', 'brand', 'sku'],
        'rich_result': 'Product snippets, Merchant listings'
    },
    'Article': {
        'required': ['headline', 'image', 'datePublished', 'author'],
        'recommended': ['dateModified', 'publisher'],
        'rich_result': 'Article rich results'
    },
    'NewsArticle': {
        'required': ['headline', 'image', 'datePublished', 'author'],
        'recommended': ['dateModified', 'publisher'],
        'rich_result': 'News rich results'
    },
    'BlogPosting': {
        'required': ['headline', 'image', 'datePublished', 'author'],
        'recommended': ['dateModified', 'publisher'],
        'rich_result': 'Article rich results'
    },
    'LocalBusiness': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'openingHours', 'image', 'priceRange', 'geo', 'url'],
        'rich_result': 'Local Business panel'
    },
    'Organization': {
        'required': ['name'],
        'recommended': ['logo', 'url', 'sameAs', 'contactPoint', 'address'],
        'rich_result': 'Knowledge Panel'
    },
    'FAQPage': {
        'required': ['mainEntity'],
        'recommended': [],
        'rich_result': 'FAQ rich results'
    },
    'HowTo': {
        'required': ['name', 'step'],
        'recommended': ['image', 'totalTime', 'estimatedCost'],
        'rich_result': 'How-to rich results'
    },
    'Recipe': {
        'required': ['name', 'image'],
        'recommended': ['author', 'datePublished', 'description', 'recipeIngredient', 'recipeInstructions', 'nutrition', 'aggregateRating'],
        'rich_result': 'Recipe rich results'
    },
    'Event': {
        'required': ['name', 'startDate', 'location'],
        'recommended': ['endDate', 'image', 'description', 'offers', 'performer', 'organizer'],
        'rich_result': 'Event rich results'
    },
    'VideoObject': {
        'required': ['name', 'description', 'thumbnailUrl', 'uploadDate'],
        'recommended': ['duration', 'contentUrl', 'embedUrl'],
        'rich_result': 'Video rich results'
    },
    'WebSite': {
        'required': ['name', 'url'],
        'recommended': ['potentialAction'],
        'rich_result': 'Sitelinks Search Box'
    },
    'WebPage': {
        'required': [],
        'recommended': ['name', 'description', 'datePublished', 'dateModified'],
        'rich_result': None
    },
    'BreadcrumbList': {
        'required': ['itemListElement'],
        'recommended': [],
        'rich_result': 'Breadcrumb trail'
    },
    'JobPosting': {
        'required': ['title', 'description', 'datePosted', 'hiringOrganization', 'jobLocation'],
        'recommended': ['validThrough', 'employmentType', 'baseSalary'],
        'rich_result': 'Job posting rich results'
    },
    'Review': {
        'required': ['itemReviewed', 'author'],
        'recommended': ['reviewRating', 'datePublished'],
        'rich_result': 'Review snippet'
    },
    'AggregateRating': {
        'required': ['ratingValue', 'ratingCount'],
        'recommended': ['bestRating', 'worstRating'],
        'rich_result': 'Star ratings'
    },
    'Course': {
        'required': ['name', 'description', 'provider'],
        'recommended': ['offers'],
        'rich_result': 'Course rich results'
    },
    'SoftwareApplication': {
        'required': ['name', 'offers'],
        'recommended': ['operatingSystem', 'applicationCategory', 'aggregateRating'],
        'rich_result': 'Software App rich results'
    },
}

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
            for entity in block['@graph']:
                entity['_source'] = f'json_ld[{block_idx}].@graph'
                entities.append(entity)
        else:
            block['_source'] = f'json_ld[{block_idx}]'
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

    parsed_url = urlparse(page_url)
    domain = f"{parsed_url.scheme}://{parsed_url.netloc}"

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


def detect_duplicate_ids(entities):
    """Detect duplicate @id definitions"""
    id_occurrences = {}

    for entity in entities:
        entity_id = entity.get('@id')
        if not entity_id:
            continue

        # Only count entities with actual properties (not just references)
        prop_count = len([k for k in entity.keys() if not k.startswith('_') and k not in ['@id', '@context']])
        if prop_count > 1:  # Has more than just @type
            if entity_id not in id_occurrences:
                id_occurrences[entity_id] = []
            id_occurrences[entity_id].append({
                'source': entity.get('_source'),
                'types': get_types_list(entity),
                'name': entity.get('name')
            })

    duplicates = []
    for id_val, occurrences in id_occurrences.items():
        if len(occurrences) > 1:
            duplicates.append({
                'id': id_val,
                'count': len(occurrences),
                'locations': [o['source'] for o in occurrences],
                'types': occurrences[0]['types']
            })

    return duplicates


def check_missing_fields(entity, entity_type):
    """Check for missing required and recommended fields"""
    requirements = RICH_RESULTS_REQUIREMENTS.get(entity_type, {})
    required = requirements.get('required', [])
    recommended = requirements.get('recommended', [])

    missing_required = []
    missing_recommended = []

    for field in required:
        if field not in entity or not entity[field]:
            missing_required.append(field)

    for field in recommended:
        if field not in entity or not entity[field]:
            missing_recommended.append(field)

    return missing_required, missing_recommended


def generate_actions(entities, identity, page_url):
    """Generate actionable items"""
    critical = []
    recommended = []
    optional = []

    # Check for duplicate IDs
    duplicates = detect_duplicate_ids(entities)
    for dup in duplicates:
        critical.append({
            'action': 'merge_duplicate_entities',
            'confidence': 'certain',
            'target': dup['id'],
            'types': dup['types'],
            'reason': f"Same @id defined {dup['count']} times",
            'impact': 'Google may misunderstand entity identity',
            'locations': dup['locations']
        })

    # Check for entities without @type
    for entity in entities:
        if not get_types_list(entity):
            critical.append({
                'action': 'add_type',
                'confidence': 'certain',
                'target': entity.get('@id', entity.get('_source')),
                'reason': 'Schema without @type is invalid',
                'impact': 'Google will ignore this schema entirely'
            })

    # Check for missing fields per entity type
    for entity in entities:
        types = get_types_list(entity)
        for entity_type in types:
            if entity_type in RICH_RESULTS_REQUIREMENTS:
                missing_req, missing_rec = check_missing_fields(entity, entity_type)

                for field in missing_req:
                    critical.append({
                        'action': 'add_required_field',
                        'confidence': 'certain',
                        'target': entity_type,
                        'field': field,
                        'entity_id': entity.get('@id'),
                        'reason': f"Required for {entity_type} validation",
                        'impact': RICH_RESULTS_REQUIREMENTS[entity_type].get('rich_result', 'Schema validation')
                    })

                for field in missing_rec:
                    recommended.append({
                        'action': 'add_recommended_field',
                        'confidence': 'certain',
                        'target': entity_type,
                        'field': field,
                        'entity_id': entity.get('@id'),
                        'reason': f"Recommended for better {entity_type} display",
                        'impact': 'Enhanced rich result appearance'
                    })

    # Check Organization identity
    if identity['organization']:
        org = identity['organization']

        # Check for missing sameAs (important for Knowledge Panel)
        same_as = org.get('same_as', {})
        if not same_as.get('wikidata'):
            recommended.append({
                'action': 'add_sameAs',
                'confidence': 'suggestion',
                'target': 'Organization',
                'platform': 'wikidata',
                'reason': 'Wikidata link helps Google verify entity identity',
                'impact': 'Higher chance for Knowledge Panel'
            })

        social = same_as.get('social', {})
        missing_social = []
        for platform in ['facebook', 'linkedin', 'instagram', 'twitter']:
            if platform not in social:
                missing_social.append(platform)

        if missing_social:
            optional.append({
                'action': 'add_sameAs',
                'confidence': 'suggestion',
                'target': 'Organization',
                'platforms': missing_social,
                'reason': 'Social profiles strengthen entity verification',
                'impact': 'Better E-E-A-T signals'
            })

        # Check for missing logo
        if not org.get('logo'):
            recommended.append({
                'action': 'add_field',
                'confidence': 'certain',
                'target': 'Organization',
                'field': 'logo',
                'reason': 'Logo is required for Knowledge Panel',
                'impact': 'No logo in search results'
            })

    # Check if Organization exists at all
    if not identity['organization']:
        found_org = any(categorize_entity(get_types_list(e)) == 'organization' for e in entities)
        if not found_org:
            recommended.append({
                'action': 'add_schema',
                'confidence': 'suggestion',
                'schema_type': 'Organization',
                'reason': 'No Organization schema found',
                'impact': 'Missing core entity identity'
            })

    # Check WebSite schema
    if identity['website']:
        if not identity['website'].get('has_search_action'):
            optional.append({
                'action': 'add_search_action',
                'confidence': 'suggestion',
                'target': 'WebSite',
                'reason': 'SearchAction enables Sitelinks Search Box',
                'impact': 'Search box in Google results'
            })
    else:
        found_website = any(categorize_entity(get_types_list(e)) == 'website' for e in entities)
        if not found_website:
            recommended.append({
                'action': 'add_schema',
                'confidence': 'suggestion',
                'schema_type': 'WebSite',
                'reason': 'No WebSite schema found',
                'impact': 'Missing site-level identity'
            })

    # Check BreadcrumbList
    found_breadcrumb = any(categorize_entity(get_types_list(e)) == 'breadcrumb' for e in entities)
    if not found_breadcrumb:
        optional.append({
            'action': 'add_schema',
            'confidence': 'suggestion',
            'schema_type': 'BreadcrumbList',
            'reason': 'BreadcrumbList shows navigation path in search results',
            'impact': 'Breadcrumb trail in search results'
        })

    return {
        'critical': critical,
        'recommended': recommended,
        'optional': optional
    }


def check_rich_results_eligibility(entities):
    """Check which Rich Results this page is eligible for"""
    eligible = []
    potential = []

    types_found = set()
    for entity in entities:
        types_found.update(get_types_list(entity))

    for entity_type, requirements in RICH_RESULTS_REQUIREMENTS.items():
        if entity_type in types_found:
            rich_result = requirements.get('rich_result')
            if rich_result:
                # Check if all required fields are present
                for entity in entities:
                    if entity_type in get_types_list(entity):
                        missing_req, _ = check_missing_fields(entity, entity_type)
                        if not missing_req:
                            if rich_result not in eligible:
                                eligible.append(rich_result)
                        else:
                            if rich_result not in potential and rich_result not in eligible:
                                potential.append(rich_result)

    return {
        'eligible': eligible,
        'potential': potential
    }


def calculate_health(actions):
    """Calculate overall health status"""
    critical_count = len(actions['critical'])
    recommended_count = len(actions['recommended'])

    if critical_count > 0:
        return 'broken'
    elif recommended_count > 3:
        return 'needs_work'
    elif recommended_count > 0:
        return 'good'
    else:
        return 'healthy'


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

        # Generate actions
        actions = generate_actions(entities, identity, url)

        # Check Rich Results eligibility
        rich_results = check_rich_results_eligibility(entities)

        # Calculate health
        health_status = calculate_health(actions)

        # Build response
        return jsonify({
            'url': url,

            'summary': {
                'health': health_status,
                'critical_issues': len(actions['critical']),
                'recommended_actions': len(actions['recommended']),
                'entities_found': len(graph['entities']),
                'json_ld_blocks': len(json_ld)
            },

            'actions': actions,

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

    try:
        html = fetch_page(url)
        base_url = get_base_url(html, url)
        metadata = extruct.extract(html, base_url=base_url)
        return jsonify(metadata)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=3015)
