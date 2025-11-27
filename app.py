from flask import Flask, request, jsonify
import requests
import extruct
from bs4 import BeautifulSoup
from w3lib.html import get_base_url
from urllib.parse import urljoin, urlparse
import re

app = Flask(__name__)
app.url_map.strict_slashes = False

# Schema.org recommended properties for common types
RECOMMENDED_PROPERTIES = {
    'Product': ['name', 'image', 'description', 'sku', 'brand', 'offers', 'review', 'aggregateRating'],
    'Article': ['headline', 'image', 'author', 'datePublished', 'dateModified', 'publisher'],
    'NewsArticle': ['headline', 'image', 'author', 'datePublished', 'dateModified', 'publisher'],
    'BlogPosting': ['headline', 'image', 'author', 'datePublished', 'dateModified', 'publisher'],
    'LocalBusiness': ['name', 'address', 'telephone', 'openingHours', 'image', 'priceRange', 'geo'],
    'Organization': ['name', 'logo', 'url', 'contactPoint', 'sameAs'],
    'Person': ['name', 'image', 'jobTitle', 'worksFor', 'sameAs'],
    'Event': ['name', 'startDate', 'endDate', 'location', 'image', 'description', 'offers', 'performer'],
    'Recipe': ['name', 'image', 'author', 'datePublished', 'description', 'recipeIngredient', 'recipeInstructions', 'nutrition'],
    'FAQPage': ['mainEntity'],
    'QAPage': ['mainEntity'],
    'HowTo': ['name', 'step', 'image', 'totalTime'],
    'WebSite': ['name', 'url', 'potentialAction'],
    'WebPage': ['name', 'description', 'breadcrumb'],
    'BreadcrumbList': ['itemListElement'],
    'Review': ['itemReviewed', 'reviewRating', 'author'],
    'AggregateRating': ['ratingValue', 'reviewCount', 'bestRating'],
    'Offer': ['price', 'priceCurrency', 'availability', 'url'],
    'VideoObject': ['name', 'description', 'thumbnailUrl', 'uploadDate', 'duration', 'contentUrl'],
    'ImageObject': ['contentUrl', 'caption'],
    'Course': ['name', 'description', 'provider'],
    'Book': ['name', 'author', 'isbn'],
    'SoftwareApplication': ['name', 'operatingSystem', 'applicationCategory', 'offers'],
    'JobPosting': ['title', 'description', 'datePosted', 'hiringOrganization', 'jobLocation'],
}

# Required properties that MUST exist for valid schemas
REQUIRED_PROPERTIES = {
    'Product': ['name'],
    'Article': ['headline'],
    'NewsArticle': ['headline'],
    'BlogPosting': ['headline'],
    'LocalBusiness': ['name'],
    'Organization': ['name'],
    'Person': ['name'],
    'Event': ['name', 'startDate'],
    'Recipe': ['name'],
    'FAQPage': ['mainEntity'],
    'Review': ['itemReviewed', 'reviewRating'],
    'Offer': ['price', 'priceCurrency'],
    'VideoObject': ['name', 'uploadDate'],
    'BreadcrumbList': ['itemListElement'],
    'JobPosting': ['title', 'hiringOrganization', 'datePosted'],
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
    metadata = extruct.extract(html, base_url=base_url, syntaxes=['json-ld', 'microdata', 'rdfa', 'opengraph'])
    return metadata


def get_schema_type(schema):
    """Get the @type from a schema, handling arrays"""
    schema_type = schema.get('@type', schema.get('type', ''))
    if isinstance(schema_type, list):
        return schema_type[0] if schema_type else ''
    return schema_type


def collect_all_ids(schemas):
    """Collect all @id values from schemas recursively"""
    ids = {}

    def traverse(obj, path='root'):
        if isinstance(obj, dict):
            if '@id' in obj:
                id_val = obj['@id']
                if id_val not in ids:
                    ids[id_val] = []
                ids[id_val].append({
                    'path': path,
                    'type': get_schema_type(obj),
                    'has_properties': len([k for k in obj.keys() if not k.startswith('@')]) > 0
                })
            for key, value in obj.items():
                traverse(value, f"{path}.{key}")
        elif isinstance(obj, list):
            for i, item in enumerate(obj):
                traverse(item, f"{path}[{i}]")

    traverse(schemas)
    return ids


def check_id_consistency(schemas):
    """Check @id consistency and references"""
    issues = []
    suggestions = []

    all_ids = collect_all_ids(schemas)

    # Check for duplicate IDs with different content
    for id_val, occurrences in all_ids.items():
        if len(occurrences) > 1:
            # Check if it's a reference vs definition issue
            definitions = [o for o in occurrences if o['has_properties']]
            references = [o for o in occurrences if not o['has_properties']]

            if len(definitions) > 1:
                issues.append({
                    'type': 'duplicate_id',
                    'severity': 'error',
                    'message': f"Duplicate @id '{id_val}' defined {len(definitions)} times",
                    'id': id_val,
                    'locations': [d['path'] for d in definitions]
                })
            elif len(definitions) == 0 and len(references) > 0:
                issues.append({
                    'type': 'orphan_reference',
                    'severity': 'warning',
                    'message': f"@id '{id_val}' is referenced but never fully defined",
                    'id': id_val
                })

    # Check for recommended @id usage
    json_ld = schemas.get('json-ld', [])
    for i, schema in enumerate(json_ld):
        schema_type = get_schema_type(schema)
        if schema_type in ['Organization', 'WebSite', 'WebPage', 'LocalBusiness', 'Person']:
            if '@id' not in schema:
                suggestions.append({
                    'type': 'missing_id',
                    'severity': 'info',
                    'message': f"{schema_type} should have @id for better linking",
                    'schema_index': i,
                    'schema_type': schema_type
                })

    return {
        'issues': issues,
        'suggestions': suggestions,
        'total_ids': len(all_ids),
        'id_map': {k: len(v) for k, v in all_ids.items()}
    }


def validate_schema(schema, index=0):
    """Validate a single schema"""
    errors = []
    warnings = []

    schema_type = get_schema_type(schema)

    # Check @type exists
    if not schema_type:
        errors.append({
            'field': '@type',
            'message': 'Missing @type property',
            'severity': 'error'
        })
        return {'errors': errors, 'warnings': warnings, 'type': 'Unknown'}

    # Check required properties
    required = REQUIRED_PROPERTIES.get(schema_type, [])
    for prop in required:
        if prop not in schema:
            errors.append({
                'field': prop,
                'message': f"Missing required property '{prop}' for {schema_type}",
                'severity': 'error'
            })
        elif not schema[prop]:
            errors.append({
                'field': prop,
                'message': f"Empty value for required property '{prop}'",
                'severity': 'error'
            })

    # Check for empty/null values in existing properties
    for key, value in schema.items():
        if value is None or value == '' or value == []:
            if key not in ['@context', '@type', '@id']:
                warnings.append({
                    'field': key,
                    'message': f"Empty value for property '{key}'",
                    'severity': 'warning'
                })

    # Validate nested schemas
    for key, value in schema.items():
        if isinstance(value, dict) and '@type' in value:
            nested_result = validate_schema(value)
            for err in nested_result['errors']:
                err['field'] = f"{key}.{err['field']}"
                errors.append(err)
            for warn in nested_result['warnings']:
                warn['field'] = f"{key}.{warn['field']}"
                warnings.append(warn)
        elif isinstance(value, list):
            for i, item in enumerate(value):
                if isinstance(item, dict) and '@type' in item:
                    nested_result = validate_schema(item)
                    for err in nested_result['errors']:
                        err['field'] = f"{key}[{i}].{err['field']}"
                        errors.append(err)
                    for warn in nested_result['warnings']:
                        warn['field'] = f"{key}[{i}].{warn['field']}"
                        warnings.append(warn)

    return {
        'errors': errors,
        'warnings': warnings,
        'type': schema_type,
        'valid': len(errors) == 0
    }


def validate_all_schemas(schemas):
    """Validate all extracted schemas"""
    results = {
        'json_ld': [],
        'microdata': [],
        'rdfa': [],
        'summary': {
            'total_schemas': 0,
            'valid_schemas': 0,
            'total_errors': 0,
            'total_warnings': 0
        }
    }

    # Validate JSON-LD
    for i, schema in enumerate(schemas.get('json-ld', [])):
        result = validate_schema(schema, i)
        result['index'] = i
        results['json_ld'].append(result)
        results['summary']['total_schemas'] += 1
        if result['valid']:
            results['summary']['valid_schemas'] += 1
        results['summary']['total_errors'] += len(result['errors'])
        results['summary']['total_warnings'] += len(result['warnings'])

    # Validate Microdata
    for i, schema in enumerate(schemas.get('microdata', [])):
        result = validate_schema(schema, i)
        result['index'] = i
        result['format'] = 'microdata'
        results['microdata'].append(result)
        results['summary']['total_schemas'] += 1
        if result['valid']:
            results['summary']['valid_schemas'] += 1
        results['summary']['total_errors'] += len(result['errors'])
        results['summary']['total_warnings'] += len(result['warnings'])

    # Validate RDFa
    for i, schema in enumerate(schemas.get('rdfa', [])):
        result = validate_schema(schema, i)
        result['index'] = i
        result['format'] = 'rdfa'
        results['rdfa'].append(result)
        results['summary']['total_schemas'] += 1
        if result['valid']:
            results['summary']['valid_schemas'] += 1
        results['summary']['total_errors'] += len(result['errors'])
        results['summary']['total_warnings'] += len(result['warnings'])

    return results


def generate_suggestions(schemas, url):
    """Generate improvement suggestions"""
    suggestions = []
    found_types = set()

    # Collect all found types
    for schema in schemas.get('json-ld', []):
        found_types.add(get_schema_type(schema))
    for schema in schemas.get('microdata', []):
        found_types.add(get_schema_type(schema))

    # Check missing recommended properties
    for schema in schemas.get('json-ld', []):
        schema_type = get_schema_type(schema)
        recommended = RECOMMENDED_PROPERTIES.get(schema_type, [])
        missing = [prop for prop in recommended if prop not in schema]

        if missing:
            suggestions.append({
                'type': 'missing_recommended',
                'schema_type': schema_type,
                'message': f"Consider adding recommended properties to {schema_type}",
                'missing_properties': missing,
                'priority': 'medium'
            })

    # Suggest common schemas if missing
    if 'WebSite' not in found_types:
        suggestions.append({
            'type': 'missing_schema',
            'schema_type': 'WebSite',
            'message': 'Consider adding WebSite schema with SearchAction for sitelinks search',
            'priority': 'low',
            'example': {
                '@type': 'WebSite',
                'name': 'Your Site Name',
                'url': url,
                'potentialAction': {
                    '@type': 'SearchAction',
                    'target': f"{url}search?q={{search_term_string}}",
                    'query-input': 'required name=search_term_string'
                }
            }
        })

    if 'BreadcrumbList' not in found_types:
        suggestions.append({
            'type': 'missing_schema',
            'schema_type': 'BreadcrumbList',
            'message': 'Consider adding BreadcrumbList for better navigation display in search results',
            'priority': 'medium'
        })

    # Check for OpenGraph completeness
    og = schemas.get('opengraph', [])
    if og:
        og_props = og[0] if og else {}
        recommended_og = ['og:title', 'og:description', 'og:image', 'og:url', 'og:type']
        missing_og = [prop for prop in recommended_og if prop not in og_props]
        if missing_og:
            suggestions.append({
                'type': 'incomplete_opengraph',
                'message': 'OpenGraph metadata is incomplete',
                'missing_properties': missing_og,
                'priority': 'medium'
            })
    else:
        suggestions.append({
            'type': 'missing_opengraph',
            'message': 'No OpenGraph metadata found - important for social sharing',
            'priority': 'high'
        })

    # Suggest JSON-LD over Microdata
    if schemas.get('microdata') and not schemas.get('json-ld'):
        suggestions.append({
            'type': 'format_recommendation',
            'message': 'Consider using JSON-LD instead of Microdata - easier to maintain and Google preferred',
            'priority': 'low'
        })

    return suggestions


def calculate_score(validation_results, id_consistency, suggestions, schemas):
    """Calculate overall schema quality score"""
    score = 100
    details = []

    # Deduct for errors (-10 each, max -40)
    error_count = validation_results['summary']['total_errors']
    error_deduction = min(error_count * 10, 40)
    if error_deduction > 0:
        score -= error_deduction
        details.append(f"-{error_deduction} points: {error_count} validation errors")

    # Deduct for warnings (-3 each, max -15)
    warning_count = validation_results['summary']['total_warnings']
    warning_deduction = min(warning_count * 3, 15)
    if warning_deduction > 0:
        score -= warning_deduction
        details.append(f"-{warning_deduction} points: {warning_count} warnings")

    # Deduct for ID issues (-5 each, max -15)
    id_issues = len(id_consistency['issues'])
    id_deduction = min(id_issues * 5, 15)
    if id_deduction > 0:
        score -= id_deduction
        details.append(f"-{id_deduction} points: {id_issues} ID consistency issues")

    # Deduct for high priority missing suggestions (-5 each, max -15)
    high_priority = len([s for s in suggestions if s.get('priority') == 'high'])
    hp_deduction = min(high_priority * 5, 15)
    if hp_deduction > 0:
        score -= hp_deduction
        details.append(f"-{hp_deduction} points: {high_priority} high priority improvements needed")

    # Bonus for having schemas (+5, max already at 100)
    if validation_results['summary']['total_schemas'] == 0:
        score -= 30
        details.append("-30 points: No structured data found")

    # Determine grade
    if score >= 90:
        grade = 'A'
    elif score >= 80:
        grade = 'B'
    elif score >= 70:
        grade = 'C'
    elif score >= 60:
        grade = 'D'
    else:
        grade = 'F'

    return {
        'score': max(0, score),
        'grade': grade,
        'details': details
    }


@app.route('/health', methods=['GET'])
def health():
    return 'OK', 200


@app.route('/analyze', methods=['POST'])
def analyze():
    """
    Comprehensive schema analysis endpoint.
    Extracts, validates, checks consistency, and suggests improvements.
    """
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({'error': 'URL is required'}), 400

    try:
        # Fetch and extract
        html = fetch_page(url)
        schemas = extract_schemas(html, url)

        # Validate
        validation_results = validate_all_schemas(schemas)

        # Check ID consistency
        id_consistency = check_id_consistency(schemas)

        # Generate suggestions
        suggestions = generate_suggestions(schemas, url)

        # Calculate score
        score_result = calculate_score(validation_results, id_consistency, suggestions, schemas)

        return jsonify({
            'url': url,
            'schemas': {
                'json_ld': schemas.get('json-ld', []),
                'microdata': schemas.get('microdata', []),
                'rdfa': schemas.get('rdfa', []),
                'opengraph': schemas.get('opengraph', [])
            },
            'validation': validation_results,
            'id_consistency': id_consistency,
            'suggestions': suggestions,
            'score': score_result
        })

    except requests.exceptions.RequestException as e:
        return jsonify({'error': f'Failed to fetch URL: {str(e)}'}), 400
    except Exception as e:
        return jsonify({'error': str(e)}), 500


# Keep legacy endpoint for backward compatibility
@app.route('/extract-schema', methods=['POST'])
def extract_schema():
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
