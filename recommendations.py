"""
Comprehensive Schema Recommendations Engine
Rich, context-aware SEO recommendations for structured data
"""

from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from enum import Enum


class Severity(Enum):
    CRITICAL = "critical"      # Schema is broken/invalid - won't work
    HIGH = "high"              # Major SEO impact - fix immediately
    MEDIUM = "medium"          # Significant improvement potential
    LOW = "low"                # Nice to have, minor impact


class Category(Enum):
    BROKEN = "broken"                    # Invalid/broken schemas
    STRUCTURAL = "structural"            # ID duplicates, broken refs
    INCOMPLETE = "incomplete"            # Missing required/recommended fields
    MISSING_SCHEMA = "missing_schema"    # Schema should exist but doesn't
    RELATIONSHIPS = "relationships"      # Entity connection issues
    OPPORTUNITY = "opportunity"          # Rich Results opportunities


@dataclass
class Recommendation:
    id: str
    title: str
    description: str
    severity: Severity
    category: Category
    impact: str
    fix: str
    schema_type: Optional[str] = None
    field: Optional[str] = None
    entity_id: Optional[str] = None
    rich_result: Optional[str] = None
    priority_score: int = 50  # 0-100, higher = more important


# =============================================================================
# GOOGLE RICH RESULTS REQUIREMENTS (Updated 2024)
# =============================================================================

SCHEMA_REQUIREMENTS = {
    'Product': {
        'required': ['name'],
        'recommended': ['image', 'description', 'brand', 'sku', 'gtin', 'mpn', 'offers'],
        'offers_required': ['price', 'priceCurrency', 'availability'],
        'offers_recommended': ['url', 'priceValidUntil', 'itemCondition'],
        'rich_result': 'Product Snippets / Merchant Listings',
        'priority': 95
    },
    'Article': {
        'required': ['headline', 'image', 'datePublished', 'author'],
        'recommended': ['dateModified', 'publisher', 'description', 'mainEntityOfPage'],
        'author_required': ['name'],
        'author_recommended': ['url', 'sameAs'],
        'rich_result': 'Article Rich Results',
        'priority': 85
    },
    'NewsArticle': {
        'required': ['headline', 'image', 'datePublished', 'author'],
        'recommended': ['dateModified', 'publisher', 'description', 'isAccessibleForFree'],
        'rich_result': 'Top Stories / News Rich Results',
        'priority': 90
    },
    'BlogPosting': {
        'required': ['headline', 'image', 'datePublished', 'author'],
        'recommended': ['dateModified', 'publisher', 'description', 'wordCount'],
        'rich_result': 'Article Rich Results',
        'priority': 80
    },
    'LocalBusiness': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'openingHoursSpecification', 'image', 'priceRange', 'geo', 'url', 'aggregateRating'],
        'address_required': ['streetAddress', 'addressLocality', 'addressCountry'],
        'address_recommended': ['postalCode', 'addressRegion'],
        'geo_required': ['latitude', 'longitude'],
        'rich_result': 'Local Business Panel / Maps',
        'priority': 95
    },
    'Organization': {
        'required': ['name'],
        'recommended': ['logo', 'url', 'sameAs', 'contactPoint', 'address', 'description'],
        'logo_recommended': ['url', 'width', 'height'],
        'rich_result': 'Knowledge Panel',
        'priority': 90
    },
    'FAQPage': {
        'required': ['mainEntity'],
        'question_required': ['name', 'acceptedAnswer'],
        'answer_required': ['text'],
        'rich_result': 'FAQ Rich Results',
        'priority': 85
    },
    'HowTo': {
        'required': ['name', 'step'],
        'recommended': ['image', 'totalTime', 'estimatedCost', 'supply', 'tool'],
        'step_required': ['text'],
        'step_recommended': ['name', 'image', 'url'],
        'rich_result': 'How-To Rich Results',
        'priority': 80
    },
    'Recipe': {
        'required': ['name', 'image'],
        'recommended': ['author', 'datePublished', 'description', 'prepTime', 'cookTime', 'totalTime',
                       'recipeYield', 'recipeIngredient', 'recipeInstructions', 'nutrition', 'aggregateRating', 'video'],
        'rich_result': 'Recipe Rich Results',
        'priority': 90
    },
    'Event': {
        'required': ['name', 'startDate', 'location'],
        'recommended': ['endDate', 'image', 'description', 'offers', 'performer', 'organizer', 'eventStatus', 'eventAttendanceMode'],
        'location_options': ['Place', 'VirtualLocation', 'PostalAddress'],
        'offers_required': ['price', 'priceCurrency', 'availability', 'url'],
        'rich_result': 'Event Rich Results',
        'priority': 85
    },
    'VideoObject': {
        'required': ['name', 'description', 'thumbnailUrl', 'uploadDate'],
        'recommended': ['duration', 'contentUrl', 'embedUrl', 'interactionStatistic', 'expires'],
        'rich_result': 'Video Rich Results / Video Carousel',
        'priority': 85
    },
    'WebSite': {
        'required': ['name', 'url'],
        'recommended': ['potentialAction', 'publisher', 'inLanguage'],
        'search_action_required': ['target', 'query-input'],
        'rich_result': 'Sitelinks Search Box',
        'priority': 80
    },
    'WebPage': {
        'required': [],
        'recommended': ['name', 'description', 'datePublished', 'dateModified', 'isPartOf', 'primaryImageOfPage'],
        'rich_result': None,
        'priority': 60
    },
    'BreadcrumbList': {
        'required': ['itemListElement'],
        'item_required': ['position', 'name'],
        'item_recommended': ['item'],
        'rich_result': 'Breadcrumb Trail',
        'priority': 75
    },
    'JobPosting': {
        'required': ['title', 'description', 'datePosted', 'hiringOrganization', 'jobLocation'],
        'recommended': ['validThrough', 'employmentType', 'baseSalary', 'identifier', 'applicantLocationRequirements'],
        'salary_required': ['currency', 'value'],
        'rich_result': 'Job Posting Rich Results',
        'priority': 90
    },
    'Review': {
        'required': ['itemReviewed', 'author'],
        'recommended': ['reviewRating', 'datePublished', 'reviewBody'],
        'rating_required': ['ratingValue'],
        'rating_recommended': ['bestRating', 'worstRating'],
        'rich_result': 'Review Snippet',
        'priority': 80
    },
    'AggregateRating': {
        'required': ['ratingValue', 'ratingCount'],
        'recommended': ['bestRating', 'worstRating', 'reviewCount'],
        'rich_result': 'Star Ratings',
        'priority': 85
    },
    'Course': {
        'required': ['name', 'description', 'provider'],
        'recommended': ['offers', 'hasCourseInstance', 'coursePrerequisites', 'educationalLevel'],
        'instance_required': ['courseMode', 'courseWorkload'],
        'rich_result': 'Course Rich Results',
        'priority': 80
    },
    'SoftwareApplication': {
        'required': ['name', 'offers'],
        'recommended': ['operatingSystem', 'applicationCategory', 'aggregateRating', 'screenshot'],
        'offers_required': ['price', 'priceCurrency'],
        'rich_result': 'Software App Rich Results',
        'priority': 75
    },
    'Person': {
        'required': ['name'],
        'recommended': ['image', 'url', 'sameAs', 'jobTitle', 'worksFor', 'description'],
        'rich_result': 'Knowledge Panel (notable persons)',
        'priority': 70
    },
    'Book': {
        'required': ['name', 'author'],
        'recommended': ['isbn', 'bookFormat', 'numberOfPages', 'publisher', 'datePublished', 'aggregateRating'],
        'rich_result': 'Book Rich Results',
        'priority': 75
    },
    'Movie': {
        'required': ['name'],
        'recommended': ['image', 'dateCreated', 'director', 'actor', 'aggregateRating', 'review', 'duration'],
        'rich_result': 'Movie Carousel',
        'priority': 75
    },
    'ItemList': {
        'required': ['itemListElement'],
        'recommended': ['numberOfItems', 'name'],
        'element_required': ['position'],
        'rich_result': 'Carousel Rich Results',
        'priority': 70
    },
    'Service': {
        'required': ['name', 'provider'],
        'recommended': ['description', 'serviceType', 'areaServed', 'offers', 'aggregateRating', 'hasOfferCatalog'],
        'rich_result': 'Service Rich Results',
        'priority': 75
    },
    'Offer': {
        'required': ['price', 'priceCurrency'],
        'recommended': ['availability', 'url', 'priceValidUntil', 'itemCondition', 'seller'],
        'rich_result': None,
        'priority': 80
    },
    # =========================================================================
    # INDUSTRY-SPECIFIC SCHEMAS
    # =========================================================================
    'Restaurant': {
        'required': ['name', 'address'],
        'recommended': ['servesCuisine', 'menu', 'telephone', 'openingHoursSpecification', 'image',
                       'priceRange', 'aggregateRating', 'review', 'acceptsReservations', 'geo'],
        'rich_result': 'Restaurant Rich Results / Local Pack',
        'priority': 90
    },
    'HealthAndBeautyBusiness': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'openingHoursSpecification', 'image', 'priceRange',
                       'aggregateRating', 'review', 'geo', 'areaServed', 'hasOfferCatalog'],
        'rich_result': 'Local Business Panel',
        'priority': 85
    },
    'MedicalBusiness': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'openingHoursSpecification', 'image', 'medicalSpecialty',
                       'aggregateRating', 'review', 'geo', 'healthPlanNetworkId', 'isAcceptingNewPatients'],
        'rich_result': 'Medical Business Panel',
        'priority': 90
    },
    'Physician': {
        'required': ['name'],
        'recommended': ['image', 'telephone', 'address', 'medicalSpecialty', 'hospitalAffiliation',
                       'aggregateRating', 'review', 'availableService'],
        'rich_result': 'Physician Panel',
        'priority': 85
    },
    'DaySpa': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'openingHoursSpecification', 'image', 'priceRange',
                       'aggregateRating', 'review', 'geo', 'hasOfferCatalog', 'amenityFeature'],
        'rich_result': 'Local Business Panel',
        'priority': 85
    },
    'BeautySalon': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'openingHoursSpecification', 'image', 'priceRange',
                       'aggregateRating', 'review', 'geo', 'hasOfferCatalog'],
        'rich_result': 'Local Business Panel',
        'priority': 85
    },
    'HomeAndConstructionBusiness': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'image', 'priceRange', 'areaServed', 'aggregateRating',
                       'review', 'geo', 'hasOfferCatalog', 'paymentAccepted'],
        'rich_result': 'Local Business Panel',
        'priority': 85
    },
    'Electrician': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'areaServed', 'aggregateRating', 'review', 'image',
                       'priceRange', 'hasOfferCatalog', 'availableService'],
        'rich_result': 'Local Business Panel',
        'priority': 85
    },
    'Plumber': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'areaServed', 'aggregateRating', 'review', 'image',
                       'priceRange', 'hasOfferCatalog', 'availableService'],
        'rich_result': 'Local Business Panel',
        'priority': 85
    },
    'RoofingContractor': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'areaServed', 'aggregateRating', 'review', 'image',
                       'priceRange', 'hasOfferCatalog'],
        'rich_result': 'Local Business Panel',
        'priority': 85
    },
    'GeneralContractor': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'areaServed', 'aggregateRating', 'review', 'image',
                       'priceRange', 'hasOfferCatalog', 'knowsAbout'],
        'rich_result': 'Local Business Panel',
        'priority': 85
    },
    'HVACBusiness': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'areaServed', 'aggregateRating', 'review', 'image',
                       'priceRange', 'hasOfferCatalog'],
        'rich_result': 'Local Business Panel',
        'priority': 85
    },
    'LodgingBusiness': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'checkinTime', 'checkoutTime', 'image', 'priceRange',
                       'aggregateRating', 'review', 'amenityFeature', 'starRating', 'numberOfRooms'],
        'rich_result': 'Hotel Rich Results',
        'priority': 90
    },
    'Hotel': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'checkinTime', 'checkoutTime', 'image', 'priceRange',
                       'aggregateRating', 'review', 'amenityFeature', 'starRating', 'numberOfRooms', 'petsAllowed'],
        'rich_result': 'Hotel Rich Results',
        'priority': 90
    },
    'RealEstateAgent': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'areaServed', 'aggregateRating', 'review', 'image', 'url'],
        'rich_result': 'Local Business Panel',
        'priority': 80
    },
    'RealEstateListing': {
        'required': ['name', 'address'],
        'recommended': ['price', 'priceCurrency', 'image', 'description', 'numberOfRooms',
                       'floorSize', 'geo', 'datePosted', 'validThrough'],
        'rich_result': 'Real Estate Listing',
        'priority': 85
    },
    'AutoDealer': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'openingHoursSpecification', 'image', 'priceRange',
                       'aggregateRating', 'review', 'geo', 'brand'],
        'rich_result': 'Auto Dealer Panel',
        'priority': 85
    },
    'AutoRepair': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'openingHoursSpecification', 'image', 'priceRange',
                       'aggregateRating', 'review', 'geo', 'areaServed'],
        'rich_result': 'Local Business Panel',
        'priority': 85
    },
    'FinancialService': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'openingHoursSpecification', 'image', 'aggregateRating',
                       'review', 'areaServed', 'hasOfferCatalog'],
        'rich_result': 'Local Business Panel',
        'priority': 80
    },
    'LegalService': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'image', 'aggregateRating', 'review', 'areaServed',
                       'knowsAbout', 'hasOfferCatalog'],
        'rich_result': 'Local Business Panel',
        'priority': 80
    },
    'Attorney': {
        'required': ['name'],
        'recommended': ['telephone', 'address', 'image', 'aggregateRating', 'review',
                       'areaServed', 'knowsAbout'],
        'rich_result': 'Attorney Panel',
        'priority': 80
    },
    'ProfessionalService': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'image', 'aggregateRating', 'review', 'areaServed',
                       'hasOfferCatalog', 'knowsAbout'],
        'rich_result': 'Local Business Panel',
        'priority': 75
    },
    # =========================================================================
    # CONTENT & MEDIA SCHEMAS
    # =========================================================================
    'Podcast': {
        'required': ['name'],
        'recommended': ['description', 'image', 'author', 'publisher', 'url', 'webFeed'],
        'rich_result': 'Podcast Rich Results',
        'priority': 80
    },
    'PodcastEpisode': {
        'required': ['name', 'url'],
        'recommended': ['description', 'datePublished', 'duration', 'associatedMedia',
                       'partOfSeries', 'episodeNumber'],
        'rich_result': 'Podcast Episode Rich Results',
        'priority': 80
    },
    'PodcastSeries': {
        'required': ['name', 'url'],
        'recommended': ['description', 'image', 'author', 'publisher', 'webFeed', 'numberOfEpisodes'],
        'rich_result': 'Podcast Series Rich Results',
        'priority': 80
    },
    'MusicRecording': {
        'required': ['name'],
        'recommended': ['byArtist', 'inAlbum', 'duration', 'isrcCode', 'datePublished'],
        'rich_result': 'Music Rich Results',
        'priority': 70
    },
    'MusicAlbum': {
        'required': ['name', 'byArtist'],
        'recommended': ['image', 'datePublished', 'numTracks', 'track', 'genre'],
        'rich_result': 'Music Album Rich Results',
        'priority': 70
    },
    'MusicGroup': {
        'required': ['name'],
        'recommended': ['image', 'genre', 'album', 'sameAs', 'description'],
        'rich_result': 'Music Artist Knowledge Panel',
        'priority': 70
    },
    'TVSeries': {
        'required': ['name'],
        'recommended': ['image', 'description', 'actor', 'director', 'numberOfSeasons',
                       'numberOfEpisodes', 'aggregateRating'],
        'rich_result': 'TV Series Carousel',
        'priority': 75
    },
    'CreativeWork': {
        'required': ['name'],
        'recommended': ['author', 'datePublished', 'description', 'image'],
        'rich_result': None,
        'priority': 60
    },
    # =========================================================================
    # EDUCATIONAL SCHEMAS
    # =========================================================================
    'EducationalOrganization': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'image', 'url', 'sameAs', 'aggregateRating', 'review'],
        'rich_result': 'Educational Organization Panel',
        'priority': 80
    },
    'CollegeOrUniversity': {
        'required': ['name', 'address'],
        'recommended': ['telephone', 'image', 'url', 'sameAs', 'aggregateRating'],
        'rich_result': 'University Knowledge Panel',
        'priority': 85
    },
    'EducationalOccupationalProgram': {
        'required': ['name', 'provider'],
        'recommended': ['description', 'timeToComplete', 'occupationalCategory', 'programType',
                       'offers', 'educationalProgramMode'],
        'rich_result': 'Program Rich Results',
        'priority': 75
    },
    # =========================================================================
    # E-COMMERCE EXTENDED
    # =========================================================================
    'ProductGroup': {
        'required': ['name'],
        'recommended': ['description', 'image', 'brand', 'hasVariant', 'variesBy'],
        'rich_result': 'Product Group Rich Results',
        'priority': 80
    },
    'OfferCatalog': {
        'required': ['name'],
        'recommended': ['itemListElement', 'numberOfItems', 'description'],
        'rich_result': None,
        'priority': 65
    },
    'ShippingDeliveryTime': {
        'required': ['handlingTime', 'transitTime'],
        'recommended': ['cutoffTime', 'businessDays'],
        'rich_result': 'Shipping Info in Product Results',
        'priority': 70
    },
    'MerchantReturnPolicy': {
        'required': ['applicableCountry', 'returnPolicyCategory'],
        'recommended': ['merchantReturnDays', 'returnMethod', 'returnFees'],
        'rich_result': 'Return Policy in Product Results',
        'priority': 70
    }
}

# =============================================================================
# PAGE TYPE DETECTION
# =============================================================================

PAGE_TYPE_INDICATORS = {
    # =========================================================================
    # GENERAL PAGE TYPES
    # =========================================================================
    'homepage': {
        'url_patterns': [r'^https?://[^/]+/?$', r'^https?://[^/]+/?(index\.html?)?$'],
        'expected_schemas': ['Organization', 'WebSite', 'WebPage'],
        'optional_schemas': ['LocalBusiness', 'ItemList']
    },
    'about': {
        'url_patterns': [r'/about', r'/about-us', r'/who-we-are', r'/our-story', r'/company'],
        'expected_schemas': ['Organization', 'WebPage', 'BreadcrumbList'],
        'optional_schemas': ['Person', 'LocalBusiness']
    },
    'contact': {
        'url_patterns': [r'/contact', r'/contact-us', r'/get-in-touch', r'/reach-us'],
        'expected_schemas': ['Organization', 'ContactPage', 'BreadcrumbList'],
        'optional_schemas': ['LocalBusiness', 'PostalAddress']
    },
    'service': {
        'url_patterns': [r'/service/', r'/services/', r'/our-services', r'/what-we-do'],
        'expected_schemas': ['Service', 'BreadcrumbList', 'Organization'],
        'optional_schemas': ['FAQPage', 'HowTo', 'Offer']
    },
    'pricing': {
        'url_patterns': [r'/pricing', r'/prices', r'/plans', r'/packages'],
        'expected_schemas': ['WebPage', 'BreadcrumbList'],
        'optional_schemas': ['Offer', 'Product', 'Service', 'FAQPage']
    },
    'landing': {
        'url_patterns': [r'/lp/', r'/landing/', r'/campaign/', r'/promo/'],
        'expected_schemas': ['WebPage'],
        'optional_schemas': ['Product', 'Service', 'Offer', 'FAQPage', 'Review']
    },
    'testimonials': {
        'url_patterns': [r'/testimonials', r'/reviews', r'/customer-stories', r'/success-stories'],
        'expected_schemas': ['WebPage', 'BreadcrumbList'],
        'optional_schemas': ['Review', 'AggregateRating', 'ItemList']
    },
    'portfolio': {
        'url_patterns': [r'/portfolio', r'/work/', r'/projects/', r'/case-stud'],
        'expected_schemas': ['WebPage', 'BreadcrumbList'],
        'optional_schemas': ['CreativeWork', 'ItemList', 'ImageGallery']
    },
    # =========================================================================
    # E-COMMERCE PAGE TYPES
    # =========================================================================
    'product': {
        'url_patterns': [r'/product/', r'/p/', r'/item/', r'/shop/.+/', r'/מוצר/'],
        'expected_schemas': ['Product', 'BreadcrumbList'],
        'optional_schemas': ['AggregateRating', 'Review', 'FAQPage', 'Offer']
    },
    'category': {
        'url_patterns': [r'/category/', r'/c/', r'/collection/', r'/קטגוריה/'],
        'expected_schemas': ['ItemList', 'BreadcrumbList', 'CollectionPage'],
        'optional_schemas': ['FAQPage', 'Product']
    },
    'collection': {
        'url_patterns': [r'/collection/', r'/collections/', r'/sale/', r'/deals/', r'/new-arrivals'],
        'expected_schemas': ['ItemList', 'BreadcrumbList', 'CollectionPage'],
        'optional_schemas': ['Offer', 'Product']
    },
    'cart': {
        'url_patterns': [r'/cart', r'/basket', r'/shopping-cart'],
        'expected_schemas': ['WebPage'],
        'optional_schemas': []
    },
    'checkout': {
        'url_patterns': [r'/checkout', r'/order', r'/payment'],
        'expected_schemas': ['WebPage'],
        'optional_schemas': []
    },
    'comparison': {
        'url_patterns': [r'/compare', r'/comparison', r'/vs/', r'-vs-'],
        'expected_schemas': ['WebPage', 'BreadcrumbList'],
        'optional_schemas': ['Product', 'ItemList']
    },
    # =========================================================================
    # CONTENT PAGE TYPES
    # =========================================================================
    'article': {
        'url_patterns': [r'/blog/', r'/article/', r'/post/', r'/news/', r'/מאמר/'],
        'expected_schemas': ['Article', 'BreadcrumbList', 'WebPage'],
        'optional_schemas': ['Person', 'FAQPage', 'HowTo', 'VideoObject']
    },
    'blog_home': {
        'url_patterns': [r'/blog/?$', r'/articles/?$', r'/news/?$'],
        'expected_schemas': ['Blog', 'BreadcrumbList', 'ItemList'],
        'optional_schemas': ['Organization']
    },
    'faq': {
        'url_patterns': [r'/faq', r'/help/', r'/support/', r'/questions/', r'/שאלות'],
        'expected_schemas': ['FAQPage', 'BreadcrumbList'],
        'optional_schemas': ['HowTo', 'Article']
    },
    'howto': {
        'url_patterns': [r'/how-to/', r'/guide/', r'/tutorial/', r'/איך-ל'],
        'expected_schemas': ['HowTo', 'BreadcrumbList'],
        'optional_schemas': ['Article', 'VideoObject', 'FAQPage']
    },
    'video': {
        'url_patterns': [r'/video/', r'/watch/', r'/v/', r'/וידאו/'],
        'expected_schemas': ['VideoObject', 'BreadcrumbList'],
        'optional_schemas': ['Article', 'HowTo', 'Course']
    },
    'podcast': {
        'url_patterns': [r'/podcast/', r'/episode/', r'/פודקאסט/'],
        'expected_schemas': ['PodcastEpisode', 'BreadcrumbList'],
        'optional_schemas': ['PodcastSeries', 'Person', 'Organization']
    },
    'person': {
        'url_patterns': [r'/author/', r'/team/', r'/staff/', r'/profile/', r'/expert/'],
        'expected_schemas': ['Person', 'WebPage', 'BreadcrumbList'],
        'optional_schemas': ['Organization', 'Article']
    },
    # =========================================================================
    # LOCAL BUSINESS PAGE TYPES
    # =========================================================================
    'local_business': {
        'url_patterns': [r'/location/', r'/store/', r'/branch/', r'/סניף/'],
        'expected_schemas': ['LocalBusiness', 'Organization', 'BreadcrumbList'],
        'optional_schemas': ['FAQPage', 'AggregateRating', 'Review']
    },
    'store_locator': {
        'url_patterns': [r'/locations', r'/stores', r'/branches', r'/find-us', r'/סניפים'],
        'expected_schemas': ['Organization', 'BreadcrumbList'],
        'optional_schemas': ['LocalBusiness', 'ItemList']
    },
    # =========================================================================
    # INDUSTRY-SPECIFIC: MEDSPA / HEALTH & BEAUTY
    # =========================================================================
    'medspa': {
        'url_patterns': [r'/medspa', r'/med-spa', r'/aesthetic', r'/מדספא', r'/אסתטיק'],
        'expected_schemas': ['HealthAndBeautyBusiness', 'Organization', 'BreadcrumbList'],
        'optional_schemas': ['MedicalBusiness', 'Service', 'FAQPage', 'AggregateRating']
    },
    'medspa_treatment': {
        'url_patterns': [r'/treatment/', r'/procedure/', r'/טיפול/', r'/botox', r'/filler', r'/laser'],
        'expected_schemas': ['Service', 'MedicalBusiness', 'BreadcrumbList'],
        'optional_schemas': ['FAQPage', 'HowTo', 'Review', 'Offer']
    },
    'beauty_salon': {
        'url_patterns': [r'/salon/', r'/beauty/', r'/hair/', r'/nail/', r'/מספרה/', r'/יופי/'],
        'expected_schemas': ['BeautySalon', 'BreadcrumbList'],
        'optional_schemas': ['Service', 'FAQPage', 'AggregateRating', 'Offer']
    },
    'spa': {
        'url_patterns': [r'/spa/', r'/wellness/', r'/massage/', r'/ספא/'],
        'expected_schemas': ['DaySpa', 'BreadcrumbList'],
        'optional_schemas': ['Service', 'FAQPage', 'AggregateRating', 'Offer']
    },
    # =========================================================================
    # INDUSTRY-SPECIFIC: HOME SERVICES / CONSTRUCTION
    # =========================================================================
    'solar': {
        'url_patterns': [r'/solar/', r'/panels/', r'/photovoltaic/', r'/סולארי/', r'/פאנלים/'],
        'expected_schemas': ['HomeAndConstructionBusiness', 'Service', 'BreadcrumbList'],
        'optional_schemas': ['FAQPage', 'HowTo', 'Review', 'Offer', 'Product']
    },
    'solar_installation': {
        'url_patterns': [r'/installation/', r'/התקנה/', r'/התקנת-פאנלים/'],
        'expected_schemas': ['Service', 'BreadcrumbList'],
        'optional_schemas': ['HowTo', 'FAQPage', 'Offer', 'Review']
    },
    'carpentry': {
        'url_patterns': [r'/carpentry/', r'/woodwork/', r'/cabinet/', r'/נגרות/', r'/נגריה/', r'/ארונות/'],
        'expected_schemas': ['HomeAndConstructionBusiness', 'Service', 'BreadcrumbList'],
        'optional_schemas': ['FAQPage', 'Review', 'Offer', 'ImageGallery']
    },
    'contractor': {
        'url_patterns': [r'/contractor/', r'/construction/', r'/renovation/', r'/remodel/', r'/שיפוץ/', r'/קבלן/'],
        'expected_schemas': ['GeneralContractor', 'Service', 'BreadcrumbList'],
        'optional_schemas': ['FAQPage', 'Review', 'Offer', 'HowTo']
    },
    'electrician': {
        'url_patterns': [r'/electrician/', r'/electrical/', r'/חשמלאי/', r'/חשמל/'],
        'expected_schemas': ['Electrician', 'Service', 'BreadcrumbList'],
        'optional_schemas': ['FAQPage', 'Review', 'Offer']
    },
    'plumber': {
        'url_patterns': [r'/plumber/', r'/plumbing/', r'/אינסטלטור/', r'/אינסטלציה/'],
        'expected_schemas': ['Plumber', 'Service', 'BreadcrumbList'],
        'optional_schemas': ['FAQPage', 'Review', 'Offer']
    },
    'hvac': {
        'url_patterns': [r'/hvac/', r'/air-conditioning/', r'/heating/', r'/מיזוג/', r'/מזגנים/'],
        'expected_schemas': ['HVACBusiness', 'Service', 'BreadcrumbList'],
        'optional_schemas': ['FAQPage', 'Review', 'Offer', 'Product']
    },
    'roofing': {
        'url_patterns': [r'/roofing/', r'/roof/', r'/גגות/', r'/איטום/'],
        'expected_schemas': ['RoofingContractor', 'Service', 'BreadcrumbList'],
        'optional_schemas': ['FAQPage', 'Review', 'Offer']
    },
    # =========================================================================
    # INDUSTRY-SPECIFIC: HOSPITALITY
    # =========================================================================
    'restaurant': {
        'url_patterns': [r'/restaurant/', r'/dining/', r'/menu/', r'/מסעדה/'],
        'expected_schemas': ['Restaurant', 'BreadcrumbList'],
        'optional_schemas': ['Menu', 'FAQPage', 'AggregateRating', 'Review']
    },
    'hotel': {
        'url_patterns': [r'/hotel/', r'/resort/', r'/accommodation/', r'/מלון/', r'/לינה/'],
        'expected_schemas': ['Hotel', 'BreadcrumbList'],
        'optional_schemas': ['FAQPage', 'AggregateRating', 'Review', 'Offer']
    },
    'room': {
        'url_patterns': [r'/room/', r'/suite/', r'/חדר/'],
        'expected_schemas': ['HotelRoom', 'BreadcrumbList'],
        'optional_schemas': ['Offer', 'AggregateRating']
    },
    # =========================================================================
    # INDUSTRY-SPECIFIC: REAL ESTATE
    # =========================================================================
    'real_estate': {
        'url_patterns': [r'/property/', r'/listing/', r'/נכס/', r'/דירה/', r'/בית/'],
        'expected_schemas': ['RealEstateListing', 'BreadcrumbList'],
        'optional_schemas': ['Place', 'Offer', 'ImageGallery']
    },
    'real_estate_agent': {
        'url_patterns': [r'/agent/', r'/realtor/', r'/תיווך/', r'/מתווך/'],
        'expected_schemas': ['RealEstateAgent', 'Person', 'BreadcrumbList'],
        'optional_schemas': ['Organization', 'Review', 'AggregateRating']
    },
    # =========================================================================
    # INDUSTRY-SPECIFIC: AUTOMOTIVE
    # =========================================================================
    'auto_dealer': {
        'url_patterns': [r'/dealer/', r'/dealership/', r'/cars/', r'/vehicles/', r'/רכב/', r'/סוכנות/'],
        'expected_schemas': ['AutoDealer', 'BreadcrumbList'],
        'optional_schemas': ['Product', 'Offer', 'AggregateRating', 'Review']
    },
    'vehicle': {
        'url_patterns': [r'/vehicle/', r'/car/', r'/auto/', r'/רכב/'],
        'expected_schemas': ['Vehicle', 'Product', 'BreadcrumbList'],
        'optional_schemas': ['Offer', 'AggregateRating', 'Review']
    },
    'auto_repair': {
        'url_patterns': [r'/repair/', r'/garage/', r'/mechanic/', r'/מוסך/', r'/תיקון/'],
        'expected_schemas': ['AutoRepair', 'BreadcrumbList'],
        'optional_schemas': ['Service', 'FAQPage', 'Review']
    },
    # =========================================================================
    # INDUSTRY-SPECIFIC: PROFESSIONAL SERVICES
    # =========================================================================
    'legal': {
        'url_patterns': [r'/attorney/', r'/lawyer/', r'/law/', r'/legal/', r'/עורך-דין/', r'/משפט/'],
        'expected_schemas': ['LegalService', 'BreadcrumbList'],
        'optional_schemas': ['Attorney', 'Person', 'FAQPage', 'Review']
    },
    'financial': {
        'url_patterns': [r'/financial/', r'/accounting/', r'/tax/', r'/רואה-חשבון/', r'/פיננסי/', r'/מס/'],
        'expected_schemas': ['FinancialService', 'BreadcrumbList'],
        'optional_schemas': ['Service', 'FAQPage', 'Review']
    },
    'medical': {
        'url_patterns': [r'/doctor/', r'/clinic/', r'/medical/', r'/health/', r'/רופא/', r'/מרפאה/'],
        'expected_schemas': ['MedicalBusiness', 'BreadcrumbList'],
        'optional_schemas': ['Physician', 'FAQPage', 'Review', 'Service']
    },
    # =========================================================================
    # INDUSTRY-SPECIFIC: EDUCATION
    # =========================================================================
    'course': {
        'url_patterns': [r'/course/', r'/class/', r'/learn/', r'/training/', r'/קורס/', r'/לימודים/'],
        'expected_schemas': ['Course', 'BreadcrumbList'],
        'optional_schemas': ['Organization', 'VideoObject', 'FAQPage', 'Review', 'Offer']
    },
    'program': {
        'url_patterns': [r'/program/', r'/degree/', r'/certification/', r'/תוכנית/'],
        'expected_schemas': ['EducationalOccupationalProgram', 'BreadcrumbList'],
        'optional_schemas': ['Course', 'Organization', 'FAQPage']
    },
    'school': {
        'url_patterns': [r'/school/', r'/academy/', r'/institute/', r'/בית-ספר/', r'/אקדמיה/'],
        'expected_schemas': ['EducationalOrganization', 'BreadcrumbList'],
        'optional_schemas': ['Course', 'FAQPage', 'Review']
    },
    # =========================================================================
    # INDUSTRY-SPECIFIC: EVENTS
    # =========================================================================
    'event': {
        'url_patterns': [r'/event/', r'/events/', r'/webinar/', r'/conference/', r'/אירוע/'],
        'expected_schemas': ['Event', 'BreadcrumbList'],
        'optional_schemas': ['Organization', 'Place', 'Offer', 'Person']
    },
    'event_venue': {
        'url_patterns': [r'/venue/', r'/hall/', r'/location/', r'/אולם/'],
        'expected_schemas': ['EventVenue', 'Place', 'BreadcrumbList'],
        'optional_schemas': ['Organization', 'FAQPage', 'Review']
    },
    # =========================================================================
    # INDUSTRY-SPECIFIC: SOFTWARE / TECH
    # =========================================================================
    'software': {
        'url_patterns': [r'/software/', r'/app/', r'/download/', r'/tool/', r'/אפליקציה/', r'/תוכנה/'],
        'expected_schemas': ['SoftwareApplication', 'BreadcrumbList'],
        'optional_schemas': ['FAQPage', 'Review', 'AggregateRating', 'Offer']
    },
    # =========================================================================
    # INDUSTRY-SPECIFIC: MEDIA & ENTERTAINMENT
    # =========================================================================
    'recipe': {
        'url_patterns': [r'/recipe/', r'/recipes/', r'/מתכון/'],
        'expected_schemas': ['Recipe', 'BreadcrumbList'],
        'optional_schemas': ['VideoObject', 'HowTo', 'ItemList', 'AggregateRating']
    },
    'book': {
        'url_patterns': [r'/book/', r'/ebook/', r'/ספר/'],
        'expected_schemas': ['Book', 'BreadcrumbList'],
        'optional_schemas': ['Review', 'AggregateRating', 'Person', 'Offer']
    },
    'music': {
        'url_patterns': [r'/music/', r'/album/', r'/song/', r'/track/', r'/מוזיקה/'],
        'expected_schemas': ['MusicRecording', 'BreadcrumbList'],
        'optional_schemas': ['MusicAlbum', 'MusicGroup', 'Person']
    },
    'movie': {
        'url_patterns': [r'/movie/', r'/film/', r'/סרט/'],
        'expected_schemas': ['Movie', 'BreadcrumbList'],
        'optional_schemas': ['Review', 'AggregateRating', 'Person', 'VideoObject']
    },
    # =========================================================================
    # CAREERS
    # =========================================================================
    'job': {
        'url_patterns': [r'/job/', r'/jobs/', r'/career/', r'/position/', r'/משרה/', r'/דרושים/'],
        'expected_schemas': ['JobPosting', 'BreadcrumbList'],
        'optional_schemas': ['Organization']
    },
    'careers_page': {
        'url_patterns': [r'/careers/?$', r'/jobs/?$', r'/דרושים/?$', r'/קריירה/?$'],
        'expected_schemas': ['WebPage', 'BreadcrumbList', 'Organization'],
        'optional_schemas': ['ItemList', 'JobPosting']
    }
}


# =============================================================================
# SOCIAL PLATFORMS FOR E-E-A-T
# =============================================================================

SOCIAL_PLATFORMS = {
    'facebook.com': {'name': 'Facebook', 'eeat_weight': 3},
    'fb.com': {'name': 'Facebook', 'eeat_weight': 3},
    'linkedin.com': {'name': 'LinkedIn', 'eeat_weight': 5},
    'twitter.com': {'name': 'Twitter/X', 'eeat_weight': 3},
    'x.com': {'name': 'Twitter/X', 'eeat_weight': 3},
    'instagram.com': {'name': 'Instagram', 'eeat_weight': 2},
    'youtube.com': {'name': 'YouTube', 'eeat_weight': 4},
    'tiktok.com': {'name': 'TikTok', 'eeat_weight': 2},
    'pinterest.com': {'name': 'Pinterest', 'eeat_weight': 1},
    'github.com': {'name': 'GitHub', 'eeat_weight': 4},
    'wikidata.org': {'name': 'Wikidata', 'eeat_weight': 10},
    'wikipedia.org': {'name': 'Wikipedia', 'eeat_weight': 8},
    'crunchbase.com': {'name': 'Crunchbase', 'eeat_weight': 6},
}


# =============================================================================
# RECOMMENDATION ENGINE
# =============================================================================

class RecommendationEngine:
    """Generates comprehensive, context-aware schema recommendations"""

    def __init__(self, entities: List[Dict], url: str, opengraph: Optional[Dict] = None):
        self.entities = entities
        self.url = url
        self.opengraph = opengraph or {}
        self.recommendations: List[Recommendation] = []

        # Pre-compute useful data
        self.types_found = self._extract_all_types()
        self.entities_by_type = self._group_by_type()
        self.ids_found = self._extract_all_ids()
        self.page_type = self._detect_page_type()
        self.identity = self._build_identity()

    def _extract_all_types(self) -> Set[str]:
        """Extract all schema types found"""
        types = set()
        for entity in self.entities:
            entity_types = self._get_types(entity)
            types.update(entity_types)
        return types

    def _group_by_type(self) -> Dict[str, List[Dict]]:
        """Group entities by their types"""
        grouped = {}
        for entity in self.entities:
            for t in self._get_types(entity):
                if t not in grouped:
                    grouped[t] = []
                grouped[t].append(entity)
        return grouped

    def _extract_all_ids(self) -> Dict[str, List[Dict]]:
        """Extract all @id values and their occurrences"""
        ids = {}
        for entity in self.entities:
            entity_id = entity.get('@id')
            if entity_id:
                if entity_id not in ids:
                    ids[entity_id] = []
                ids[entity_id].append(entity)
        return ids

    def _get_types(self, entity: Dict) -> List[str]:
        """Get @type as list"""
        t = entity.get('@type', entity.get('type', []))
        if isinstance(t, str):
            return [t]
        return t if t else []

    def _detect_page_type(self) -> str:
        """Detect page type from URL and content"""
        import re
        url_lower = self.url.lower()

        for page_type, indicators in PAGE_TYPE_INDICATORS.items():
            for pattern in indicators['url_patterns']:
                if re.search(pattern, url_lower):
                    return page_type

        # Fallback: detect from schemas present
        if 'Product' in self.types_found:
            return 'product'
        if any(t in self.types_found for t in ['Article', 'NewsArticle', 'BlogPosting']):
            return 'article'
        if 'Recipe' in self.types_found:
            return 'recipe'
        if 'LocalBusiness' in self.types_found or any('Business' in t for t in self.types_found):
            return 'local_business'
        if 'Event' in self.types_found:
            return 'event'
        if 'JobPosting' in self.types_found:
            return 'job'
        if 'FAQPage' in self.types_found:
            return 'faq'
        if 'VideoObject' in self.types_found:
            return 'video'

        # Check if homepage
        import re
        if re.match(r'^https?://[^/]+/?$', self.url):
            return 'homepage'

        return 'generic'

    def _build_identity(self) -> Dict:
        """Build identity information"""
        identity = {
            'organization': None,
            'website': None,
            'page': None,
            'author': None
        }

        for entity in self.entities:
            types = self._get_types(entity)
            types_lower = [t.lower() for t in types]

            if any('organization' in t or 'business' in t for t in types_lower):
                if not identity['organization']:
                    identity['organization'] = entity

            if any('website' in t for t in types_lower):
                if not identity['website']:
                    identity['website'] = entity

            if any('webpage' in t for t in types_lower):
                if not identity['page']:
                    identity['page'] = entity

            if any('person' in t for t in types_lower):
                if not identity['author']:
                    identity['author'] = entity

        return identity

    def _add(self, rec: Recommendation):
        """Add a recommendation"""
        self.recommendations.append(rec)

    def analyze(self) -> Dict[str, Any]:
        """Run full analysis and return results"""
        # Run all checks
        self._check_critical_issues()
        self._check_structural_issues()
        self._check_incomplete_schemas()
        self._check_missing_schemas()
        self._check_relationship_issues()
        self._check_opportunities()
        self._check_eeat_signals()

        # Sort by priority
        self.recommendations.sort(key=lambda r: r.priority_score, reverse=True)

        # Group by category
        grouped = {
            'critical': [],
            'high': [],
            'medium': [],
            'low': []
        }

        for rec in self.recommendations:
            grouped[rec.severity.value if rec.severity != Severity.CRITICAL else 'critical'].append({
                'id': rec.id,
                'title': rec.title,
                'description': rec.description,
                'category': rec.category.value,
                'impact': rec.impact,
                'fix': rec.fix,
                'schema_type': rec.schema_type,
                'field': rec.field,
                'entity_id': rec.entity_id,
                'rich_result': rec.rich_result,
                'priority': rec.priority_score
            })

        return {
            'page_type': self.page_type,
            'schemas_found': list(self.types_found),
            'total_issues': len(self.recommendations),
            'by_severity': {
                'critical': len(grouped['critical']),
                'high': len(grouped['high']),
                'medium': len(grouped['medium']),
                'low': len(grouped['low'])
            },
            'recommendations': grouped
        }

    # =========================================================================
    # CRITICAL ISSUES - Schema is broken/invalid
    # =========================================================================

    def _check_critical_issues(self):
        """Check for critical schema issues"""

        # 1. Entities without @type
        for entity in self.entities:
            if not self._get_types(entity):
                self._add(Recommendation(
                    id='missing_type',
                    title='סכמה ללא @type',
                    description='נמצאה סכמה ללא הגדרת סוג (@type). Google לא יזהה את הסכמה הזו.',
                    severity=Severity.CRITICAL,
                    category=Category.BROKEN,
                    impact='הסכמה תתעלם לחלוטין על ידי Google',
                    fix='הוסף שדה @type עם סוג הסכמה המתאים',
                    entity_id=entity.get('@id', entity.get('_source')),
                    priority_score=100
                ))

        # 2. Invalid @type values
        valid_types = set(SCHEMA_REQUIREMENTS.keys())
        for entity in self.entities:
            for t in self._get_types(entity):
                # Check for common typos
                if t.lower() in ['organisations', 'organisation', 'artical', 'prodcut']:
                    self._add(Recommendation(
                        id='typo_in_type',
                        title=f'שגיאת כתיב ב-@type: {t}',
                        description=f'הסוג "{t}" נראה כמו שגיאת כתיב. Google לא יזהה סוגים לא תקניים.',
                        severity=Severity.CRITICAL,
                        category=Category.BROKEN,
                        impact='הסכמה לא תזוהה ולא תופיע ב-Rich Results',
                        fix=f'תקן ל-@type הנכון (לדוגמה: Organization, Article, Product)',
                        schema_type=t,
                        entity_id=entity.get('@id'),
                        priority_score=100
                    ))

        # 3. Missing required fields
        for schema_type, requirements in SCHEMA_REQUIREMENTS.items():
            if schema_type in self.entities_by_type:
                for entity in self.entities_by_type[schema_type]:
                    for field in requirements.get('required', []):
                        if not entity.get(field):
                            self._add(Recommendation(
                                id=f'missing_required_{schema_type}_{field}',
                                title=f'{schema_type}: חסר שדה חובה "{field}"',
                                description=f'השדה {field} הוא שדה חובה עבור {schema_type} לפי דרישות Google.',
                                severity=Severity.CRITICAL,
                                category=Category.BROKEN,
                                impact=f'הסכמה לא תעבור validation ולא תזכה ב-{requirements.get("rich_result", "Rich Results")}',
                                fix=f'הוסף את השדה {field} עם ערך תקין',
                                schema_type=schema_type,
                                field=field,
                                entity_id=entity.get('@id'),
                                rich_result=requirements.get('rich_result'),
                                priority_score=95
                            ))

        # 4. Empty required nested objects
        self._check_empty_nested_objects()

        # 5. Invalid date formats
        self._check_date_formats()

        # 6. Invalid URL formats
        self._check_url_formats()

        # 7. Invalid price/currency formats
        self._check_price_formats()

    def _check_empty_nested_objects(self):
        """Check for empty nested objects that should have content"""
        nested_checks = [
            ('Product', 'offers', ['price', 'priceCurrency']),
            ('Article', 'author', ['name']),
            ('Article', 'publisher', ['name']),
            ('LocalBusiness', 'address', ['streetAddress', 'addressLocality']),
            ('LocalBusiness', 'geo', ['latitude', 'longitude']),
            ('Event', 'location', ['name', 'address']),
            ('FAQPage', 'mainEntity', ['name', 'acceptedAnswer']),
            ('Review', 'reviewRating', ['ratingValue']),
            ('AggregateRating', 'ratingValue', []),
        ]

        for schema_type, field, required_subfields in nested_checks:
            if schema_type in self.entities_by_type:
                for entity in self.entities_by_type[schema_type]:
                    nested = entity.get(field)
                    if nested:
                        if isinstance(nested, dict):
                            nested_list = [nested]
                        elif isinstance(nested, list):
                            nested_list = nested
                        else:
                            continue

                        for idx, nested_obj in enumerate(nested_list):
                            if isinstance(nested_obj, dict):
                                for subfield in required_subfields:
                                    if not nested_obj.get(subfield):
                                        self._add(Recommendation(
                                            id=f'empty_nested_{schema_type}_{field}_{subfield}',
                                            title=f'{schema_type}.{field}: חסר {subfield}',
                                            description=f'האובייקט {field} קיים אבל חסר בו השדה {subfield} שהוא חובה.',
                                            severity=Severity.CRITICAL,
                                            category=Category.BROKEN,
                                            impact='הסכמה חלקית - Google עלול להתעלם ממנה',
                                            fix=f'הוסף את השדה {subfield} לאובייקט {field}',
                                            schema_type=schema_type,
                                            field=f'{field}.{subfield}',
                                            entity_id=entity.get('@id'),
                                            priority_score=93
                                        ))

    def _check_date_formats(self):
        """Check for invalid date formats"""
        import re
        date_fields = ['datePublished', 'dateModified', 'startDate', 'endDate', 'uploadDate', 'datePosted', 'validThrough']
        valid_date_pattern = r'^\d{4}-\d{2}-\d{2}(T\d{2}:\d{2}(:\d{2})?(Z|[+-]\d{2}:\d{2})?)?$'

        for entity in self.entities:
            for field in date_fields:
                value = entity.get(field)
                if value and isinstance(value, str):
                    if not re.match(valid_date_pattern, value):
                        self._add(Recommendation(
                            id=f'invalid_date_{field}',
                            title=f'פורמט תאריך לא תקין: {field}',
                            description=f'הערך "{value}" אינו בפורמט ISO 8601 תקין.',
                            severity=Severity.CRITICAL,
                            category=Category.BROKEN,
                            impact='Google לא יפרש את התאריך נכון',
                            fix='השתמש בפורמט ISO 8601: YYYY-MM-DD או YYYY-MM-DDTHH:MM:SSZ',
                            field=field,
                            entity_id=entity.get('@id'),
                            priority_score=90
                        ))

    def _check_url_formats(self):
        """Check for invalid URL formats"""
        import re
        url_fields = ['url', 'image', 'logo', 'sameAs', 'mainEntityOfPage', 'contentUrl', 'embedUrl', 'thumbnailUrl']

        for entity in self.entities:
            for field in url_fields:
                value = entity.get(field)
                if value:
                    urls = value if isinstance(value, list) else [value]
                    for url in urls:
                        if isinstance(url, str) and url and not url.startswith(('http://', 'https://', '/')):
                            # Check if it's a dict with url inside
                            if not isinstance(url, dict):
                                self._add(Recommendation(
                                    id=f'invalid_url_{field}',
                                    title=f'URL לא תקין בשדה {field}',
                                    description=f'הערך "{url[:50]}..." אינו URL תקין.',
                                    severity=Severity.HIGH,
                                    category=Category.BROKEN,
                                    impact='קישורים שבורים עלולים לפגוע באמינות הסכמה',
                                    fix='השתמש ב-URL מלא שמתחיל ב-https://',
                                    field=field,
                                    entity_id=entity.get('@id'),
                                    priority_score=85
                                ))

    def _check_price_formats(self):
        """Check for invalid price/currency formats"""
        for entity in self.entities:
            types = self._get_types(entity)

            # Check Offer schemas
            if 'Offer' in types or entity.get('offers'):
                offers = entity.get('offers', entity)
                if isinstance(offers, dict):
                    offers = [offers]
                elif not isinstance(offers, list):
                    offers = []

                for offer in offers:
                    if isinstance(offer, dict):
                        price = offer.get('price')
                        currency = offer.get('priceCurrency')

                        if price is not None:
                            # Check if price is a valid number
                            if isinstance(price, str):
                                # Remove currency symbols and check
                                cleaned = price.replace('$', '').replace('€', '').replace('₪', '').replace(',', '')
                                try:
                                    float(cleaned)
                                except ValueError:
                                    self._add(Recommendation(
                                        id='invalid_price_format',
                                        title='פורמט מחיר לא תקין',
                                        description=f'הערך "{price}" אינו מספר תקין. המחיר צריך להיות מספר בלבד.',
                                        severity=Severity.HIGH,
                                        category=Category.BROKEN,
                                        impact='Google לא יציג את המחיר ב-Rich Results',
                                        fix='השתמש במספר בלבד (לדוגמה: 99.99) והגדר את המטבע בשדה priceCurrency',
                                        field='price',
                                        entity_id=entity.get('@id'),
                                        priority_score=88
                                    ))

                        if currency and len(currency) != 3:
                            self._add(Recommendation(
                                id='invalid_currency_format',
                                title='קוד מטבע לא תקין',
                                description=f'הערך "{currency}" אינו קוד מטבע ISO 4217 תקין.',
                                severity=Severity.HIGH,
                                category=Category.BROKEN,
                                impact='Google לא יציג את המחיר נכון',
                                fix='השתמש בקוד מטבע ISO 4217 (לדוגמה: USD, EUR, ILS)',
                                field='priceCurrency',
                                entity_id=entity.get('@id'),
                                priority_score=88
                            ))

    # =========================================================================
    # STRUCTURAL ISSUES - Duplicates, broken refs, orphans
    # =========================================================================

    def _check_structural_issues(self):
        """Check for structural problems in schema graph"""

        # 1. Duplicate @id definitions
        for entity_id, occurrences in self.ids_found.items():
            # Count only entities with actual content (not just references)
            full_entities = [e for e in occurrences if len([k for k in e.keys() if not k.startswith('_') and k not in ['@id', '@context', '@type']]) > 0]
            if len(full_entities) > 1:
                types = self._get_types(full_entities[0])
                self._add(Recommendation(
                    id='duplicate_id',
                    title=f'@id כפול: {entity_id[:50]}',
                    description=f'אותו @id מוגדר {len(full_entities)} פעמים עם תוכן שונה. זה יוצר בלבול עבור Google.',
                    severity=Severity.HIGH,
                    category=Category.STRUCTURAL,
                    impact='Google עלול לערבב בין הישויות או להתעלם מהן',
                    fix='מזג את ההגדרות לישות אחת או השתמש ב-@id ייחודי לכל ישות',
                    entity_id=entity_id,
                    schema_type=types[0] if types else None,
                    priority_score=90
                ))

        # 2. Broken @id references
        self._check_broken_references()

        # 3. Orphaned entities (no connections)
        self._check_orphaned_entities()

        # 4. Multiple Organizations without hierarchy
        self._check_multiple_organizations()

        # 5. Conflicting information
        self._check_conflicting_info()

    def _check_broken_references(self):
        """Check for @id references that don't resolve"""
        all_ids = set(self.ids_found.keys())
        ref_fields = ['isPartOf', 'publisher', 'author', 'about', 'mainEntity', 'provider',
                      'organizer', 'performer', 'itemReviewed', 'parentOrganization', 'subOrganization', 'memberOf', 'mainEntityOfPage']

        for entity in self.entities:
            for field in ref_fields:
                value = entity.get(field)
                if isinstance(value, dict):
                    ref_id = value.get('@id')
                    if ref_id and ref_id not in all_ids and not ref_id.startswith('http'):
                        # This is a local reference that doesn't exist
                        self._add(Recommendation(
                            id=f'broken_ref_{field}',
                            title=f'הפניה שבורה: {field}',
                            description=f'השדה {field} מפנה ל-@id "{ref_id}" שלא קיים בסכמות.',
                            severity=Severity.HIGH,
                            category=Category.STRUCTURAL,
                            impact='הקשר בין הישויות לא יזוהה על ידי Google',
                            fix=f'הגדר ישות עם @id "{ref_id}" או הסר את ההפניה',
                            field=field,
                            entity_id=entity.get('@id'),
                            priority_score=85
                        ))

    def _check_orphaned_entities(self):
        """Check for entities that have no connections"""
        connected_ids = set()
        ref_fields = ['isPartOf', 'publisher', 'author', 'about', 'mainEntity', 'provider', 'organizer', 'performer']

        # Find all referenced IDs
        for entity in self.entities:
            for field in ref_fields:
                value = entity.get(field)
                if isinstance(value, dict):
                    ref_id = value.get('@id')
                    if ref_id:
                        connected_ids.add(ref_id)
                elif isinstance(value, str) and value.startswith('#'):
                    connected_ids.add(value)

        # Check for important orphaned entities
        important_types = {'Organization', 'LocalBusiness', 'Person', 'WebSite'}
        for entity in self.entities:
            entity_id = entity.get('@id')
            types = set(self._get_types(entity))

            if entity_id and types & important_types:
                if entity_id not in connected_ids:
                    # Check if this entity references others
                    has_outgoing = any(entity.get(f) for f in ref_fields)
                    if not has_outgoing:
                        self._add(Recommendation(
                            id='orphaned_entity',
                            title=f'ישות מנותקת: {list(types & important_types)[0]}',
                            description=f'הישות {entity_id} לא מקושרת לאף ישות אחרת בגרף.',
                            severity=Severity.MEDIUM,
                            category=Category.STRUCTURAL,
                            impact='Google עלול לא להבין את הקשר בין הישויות',
                            fix='קשר את הישות לישויות אחרות באמצעות שדות כמו publisher, author, isPartOf',
                            entity_id=entity_id,
                            schema_type=list(types)[0],
                            priority_score=70
                        ))

    def _check_multiple_organizations(self):
        """Check for multiple organizations without clear hierarchy"""
        org_types = ['Organization', 'LocalBusiness', 'Corporation', 'NGO']
        orgs = []
        for entity in self.entities:
            types = self._get_types(entity)
            if any(t in types or any(ot in t for ot in ['Organization', 'Business']) for t in types):
                orgs.append(entity)

        if len(orgs) > 1:
            # Check if they have parent/child relationships
            has_hierarchy = any(
                org.get('parentOrganization') or org.get('subOrganization')
                for org in orgs
            )
            if not has_hierarchy:
                self._add(Recommendation(
                    id='multiple_orgs_no_hierarchy',
                    title='מספר ארגונים ללא היררכיה',
                    description=f'נמצאו {len(orgs)} ארגונים ללא קשר parentOrganization/subOrganization ביניהם.',
                    severity=Severity.MEDIUM,
                    category=Category.STRUCTURAL,
                    impact='Google עלול להתבלבל לגבי הישות הראשית',
                    fix='הגדר קשרי parentOrganization/subOrganization או הסר ארגונים מיותרים',
                    priority_score=65
                ))

    def _check_conflicting_info(self):
        """Check for conflicting information between schemas"""
        # Check if Organization name matches WebSite name
        org = self.identity.get('organization')
        website = self.identity.get('website')

        if org and website:
            org_name = org.get('name', '').lower().strip()
            site_name = website.get('name', '').lower().strip()
            if org_name and site_name and org_name != site_name:
                # They don't match - might be intentional but worth flagging
                self._add(Recommendation(
                    id='name_mismatch_org_website',
                    title='אי-התאמה בשם: Organization vs WebSite',
                    description=f'שם הארגון "{org.get("name")}" שונה משם האתר "{website.get("name")}".',
                    severity=Severity.LOW,
                    category=Category.STRUCTURAL,
                    impact='עלול ליצור בלבול לגבי זהות המותג',
                    fix='ודא שהשמות עקביים או שההבדל מכוון',
                    priority_score=40
                ))

    # =========================================================================
    # INCOMPLETE SCHEMAS - Missing recommended fields
    # =========================================================================

    def _check_incomplete_schemas(self):
        """Check for missing recommended fields"""

        for schema_type, requirements in SCHEMA_REQUIREMENTS.items():
            if schema_type in self.entities_by_type:
                for entity in self.entities_by_type[schema_type]:
                    # Check recommended fields
                    for field in requirements.get('recommended', []):
                        if not entity.get(field):
                            priority = requirements.get('priority', 50) - 10
                            self._add(Recommendation(
                                id=f'missing_recommended_{schema_type}_{field}',
                                title=f'{schema_type}: מומלץ להוסיף "{field}"',
                                description=f'השדה {field} מומלץ על ידי Google עבור {schema_type} לתצוגה מיטבית.',
                                severity=Severity.MEDIUM,
                                category=Category.INCOMPLETE,
                                impact=f'שיפור התצוגה ב-{requirements.get("rich_result", "תוצאות החיפוש")}',
                                fix=f'הוסף את השדה {field} עם ערך רלוונטי',
                                schema_type=schema_type,
                                field=field,
                                entity_id=entity.get('@id'),
                                rich_result=requirements.get('rich_result'),
                                priority_score=priority
                            ))

                    # Check nested object recommended fields
                    self._check_nested_recommended(entity, schema_type, requirements)

    def _check_nested_recommended(self, entity: Dict, schema_type: str, requirements: Dict):
        """Check recommended fields in nested objects"""
        nested_checks = {
            'offers': ('offers_recommended', ['url', 'priceValidUntil', 'itemCondition', 'seller']),
            'author': ('author_recommended', ['url', 'sameAs']),
            'address': ('address_recommended', ['postalCode', 'addressRegion']),
        }

        for field, (req_key, subfields) in nested_checks.items():
            nested = entity.get(field)
            if nested and req_key in requirements:
                if isinstance(nested, dict):
                    for subfield in requirements.get(req_key, []):
                        if not nested.get(subfield):
                            self._add(Recommendation(
                                id=f'nested_recommended_{schema_type}_{field}_{subfield}',
                                title=f'{schema_type}.{field}: מומלץ להוסיף "{subfield}"',
                                description=f'השדה {subfield} בתוך {field} מומלץ לתצוגה מלאה.',
                                severity=Severity.LOW,
                                category=Category.INCOMPLETE,
                                impact='תצוגה עשירה יותר ב-Rich Results',
                                fix=f'הוסף את השדה {subfield} לאובייקט {field}',
                                schema_type=schema_type,
                                field=f'{field}.{subfield}',
                                entity_id=entity.get('@id'),
                                priority_score=50
                            ))

    # =========================================================================
    # MISSING SCHEMAS - Schemas that should exist based on context
    # =========================================================================

    def _check_missing_schemas(self):
        """Check for schemas that should exist based on page type"""
        page_config = PAGE_TYPE_INDICATORS.get(self.page_type, {})
        expected = page_config.get('expected_schemas', [])
        optional = page_config.get('optional_schemas', [])

        # Check expected schemas
        for schema_type in expected:
            if schema_type not in self.types_found:
                # Check for similar types (e.g., LocalBusiness instead of Organization)
                if schema_type == 'Organization' and any('Business' in t or 'Organization' in t for t in self.types_found):
                    continue
                if schema_type == 'Article' and any(t in self.types_found for t in ['NewsArticle', 'BlogPosting']):
                    continue

                req = SCHEMA_REQUIREMENTS.get(schema_type, {})
                self._add(Recommendation(
                    id=f'missing_schema_{schema_type}',
                    title=f'חסרה סכמת {schema_type}',
                    description=f'לפי סוג העמוד ({self.page_type}), מצופה שתהיה סכמת {schema_type}.',
                    severity=Severity.HIGH,
                    category=Category.MISSING_SCHEMA,
                    impact=req.get('rich_result', 'זיהוי תוכן על ידי Google'),
                    fix=f'הוסף סכמת {schema_type} עם השדות הנדרשים: {", ".join(req.get("required", []))}',
                    schema_type=schema_type,
                    rich_result=req.get('rich_result'),
                    priority_score=req.get('priority', 70)
                ))

        # Check optional schemas (lower priority)
        for schema_type in optional:
            if schema_type not in self.types_found:
                req = SCHEMA_REQUIREMENTS.get(schema_type, {})
                if req.get('rich_result'):  # Only suggest if has Rich Result
                    self._add(Recommendation(
                        id=f'optional_schema_{schema_type}',
                        title=f'הזדמנות: סכמת {schema_type}',
                        description=f'סכמת {schema_type} יכולה לשפר את התצוגה עבור סוג עמוד זה.',
                        severity=Severity.LOW,
                        category=Category.OPPORTUNITY,
                        impact=req.get('rich_result'),
                        fix=f'שקול להוסיף סכמת {schema_type}',
                        schema_type=schema_type,
                        rich_result=req.get('rich_result'),
                        priority_score=req.get('priority', 50) - 20
                    ))

        # Universal checks - schemas that should exist on most pages
        self._check_universal_schemas()

    def _check_universal_schemas(self):
        """Check for schemas that should exist on most pages"""

        # Organization should exist somewhere
        has_org = any('Organization' in t or 'Business' in t for t in self.types_found)
        if not has_org and self.page_type != 'generic':
            self._add(Recommendation(
                id='missing_organization',
                title='חסרה סכמת Organization',
                description='סכמת Organization היא בסיסית לזיהוי העסק/מותג שלך על ידי Google.',
                severity=Severity.MEDIUM,
                category=Category.MISSING_SCHEMA,
                impact='Knowledge Panel, E-E-A-T signals',
                fix='הוסף סכמת Organization עם name, logo, url, sameAs',
                schema_type='Organization',
                rich_result='Knowledge Panel',
                priority_score=80
            ))

        # WebSite should exist on homepage or globally
        if 'WebSite' not in self.types_found and self.page_type == 'homepage':
            self._add(Recommendation(
                id='missing_website',
                title='חסרה סכמת WebSite',
                description='סכמת WebSite מאפשרת הצגת תיבת חיפוש באתר בתוצאות Google.',
                severity=Severity.MEDIUM,
                category=Category.MISSING_SCHEMA,
                impact='Sitelinks Search Box',
                fix='הוסף סכמת WebSite עם name, url, ו-potentialAction (SearchAction)',
                schema_type='WebSite',
                rich_result='Sitelinks Search Box',
                priority_score=75
            ))

        # BreadcrumbList for non-homepage
        if 'BreadcrumbList' not in self.types_found and self.page_type not in ['homepage', 'generic']:
            self._add(Recommendation(
                id='missing_breadcrumb',
                title='חסרה סכמת BreadcrumbList',
                description='BreadcrumbList מציגה נתיב ניווט בתוצאות החיפוש.',
                severity=Severity.LOW,
                category=Category.MISSING_SCHEMA,
                impact='Breadcrumb trail בתוצאות',
                fix='הוסף סכמת BreadcrumbList עם itemListElement',
                schema_type='BreadcrumbList',
                rich_result='Breadcrumb Trail',
                priority_score=65
            ))

    # =========================================================================
    # RELATIONSHIP ISSUES
    # =========================================================================

    def _check_relationship_issues(self):
        """Check for missing or incorrect entity relationships"""

        # Article without proper author connection
        article_types = ['Article', 'NewsArticle', 'BlogPosting']
        for article_type in article_types:
            if article_type in self.entities_by_type:
                for article in self.entities_by_type[article_type]:
                    author = article.get('author')
                    if author:
                        if isinstance(author, dict):
                            # Check if author has proper Person schema
                            author_type = author.get('@type')
                            if not author_type:
                                self._add(Recommendation(
                                    id='author_missing_type',
                                    title='Author ללא @type',
                                    description='האובייקט author צריך להיות מסוג Person או Organization.',
                                    severity=Severity.HIGH,
                                    category=Category.RELATIONSHIPS,
                                    impact='Google לא יזהה את המחבר כישות',
                                    fix='הוסף @type: "Person" לאובייקט author',
                                    schema_type=article_type,
                                    field='author',
                                    entity_id=article.get('@id'),
                                    priority_score=80
                                ))
                            # Check if author has URL/sameAs for E-E-A-T
                            if not author.get('url') and not author.get('sameAs'):
                                self._add(Recommendation(
                                    id='author_no_url',
                                    title='Author ללא קישור לפרופיל',
                                    description='המחבר חסר url או sameAs לאימות זהות.',
                                    severity=Severity.MEDIUM,
                                    category=Category.RELATIONSHIPS,
                                    impact='E-E-A-T: קשה לאמת את המומחיות של המחבר',
                                    fix='הוסף url לדף המחבר באתר או sameAs לפרופילים חברתיים',
                                    schema_type=article_type,
                                    field='author.url',
                                    entity_id=article.get('@id'),
                                    priority_score=70
                                ))
                        elif isinstance(author, str) and not author.startswith('#'):
                            # Just a name string, not a proper reference
                            self._add(Recommendation(
                                id='author_just_string',
                                title='Author כטקסט במקום אובייקט',
                                description=f'השדה author מכיל רק טקסט ("{author}") במקום אובייקט Person מלא.',
                                severity=Severity.MEDIUM,
                                category=Category.RELATIONSHIPS,
                                impact='Google לא יזהה את המחבר כישות E-E-A-T',
                                fix='הפוך את author לאובייקט עם @type: "Person", name, url',
                                schema_type=article_type,
                                field='author',
                                entity_id=article.get('@id'),
                                priority_score=75
                            ))

        # Publisher connection
        for article_type in article_types:
            if article_type in self.entities_by_type:
                for article in self.entities_by_type[article_type]:
                    publisher = article.get('publisher')
                    if publisher and isinstance(publisher, dict):
                        if not publisher.get('logo'):
                            self._add(Recommendation(
                                id='publisher_no_logo',
                                title='Publisher ללא logo',
                                description='הארגון המפרסם חסר logo - נדרש עבור News Rich Results.',
                                severity=Severity.HIGH,
                                category=Category.RELATIONSHIPS,
                                impact='לא יופיע ב-Google News / Top Stories',
                                fix='הוסף logo לאובייקט publisher',
                                schema_type=article_type,
                                field='publisher.logo',
                                entity_id=article.get('@id'),
                                priority_score=85
                            ))
                    elif not publisher:
                        self._add(Recommendation(
                            id='article_no_publisher',
                            title=f'{article_type} ללא publisher',
                            description='מאמר ללא הגדרת publisher מפסיד זכאות ל-Rich Results.',
                            severity=Severity.HIGH,
                            category=Category.RELATIONSHIPS,
                            impact='לא יהיה זכאי ל-Article Rich Results',
                            fix='הוסף publisher עם @type: "Organization", name, logo',
                            schema_type=article_type,
                            field='publisher',
                            entity_id=article.get('@id'),
                            priority_score=80
                        ))

        # Product without brand
        if 'Product' in self.entities_by_type:
            for product in self.entities_by_type['Product']:
                if not product.get('brand'):
                    self._add(Recommendation(
                        id='product_no_brand',
                        title='Product ללא brand',
                        description='מוצר ללא מותג מקשה על Google לזהות ולהשוות מוצרים.',
                        severity=Severity.MEDIUM,
                        category=Category.RELATIONSHIPS,
                        impact='תצוגה פחות עשירה ב-Shopping results',
                        fix='הוסף brand עם @type: "Brand" ו-name',
                        schema_type='Product',
                        field='brand',
                        entity_id=product.get('@id'),
                        priority_score=70
                    ))

    # =========================================================================
    # OPPORTUNITIES - Rich Results and optimizations
    # =========================================================================

    def _check_opportunities(self):
        """Check for Rich Results opportunities"""

        # FAQPage opportunity for content pages
        if self.page_type in ['article', 'product', 'local_business'] and 'FAQPage' not in self.types_found:
            self._add(Recommendation(
                id='opportunity_faq',
                title='הזדמנות: הוסף FAQPage',
                description='דפי FAQ מקבלים נדל"ן משמעותי בתוצאות החיפוש.',
                severity=Severity.LOW,
                category=Category.OPPORTUNITY,
                impact='FAQ Rich Results - עד 3-4 שאלות בתוצאות',
                fix='הוסף סכמת FAQPage עם 3-10 שאלות ותשובות רלוונטיות',
                schema_type='FAQPage',
                rich_result='FAQ Rich Results',
                priority_score=60
            ))

        # HowTo opportunity for articles
        if self.page_type == 'article' and 'HowTo' not in self.types_found:
            self._add(Recommendation(
                id='opportunity_howto',
                title='הזדמנות: הוסף HowTo',
                description='אם התוכן מסביר איך לעשות משהו, HowTo יכול להציג צעדים בתוצאות.',
                severity=Severity.LOW,
                category=Category.OPPORTUNITY,
                impact='How-To Rich Results עם צעדים',
                fix='אם רלוונטי, הוסף סכמת HowTo עם step-by-step',
                schema_type='HowTo',
                rich_result='How-To Rich Results',
                priority_score=50
            ))

        # Video opportunity
        if 'VideoObject' not in self.types_found:
            # Check if page might have video (from OpenGraph)
            if self.opengraph.get('type') == 'video' or self.opengraph.get('video'):
                self._add(Recommendation(
                    id='opportunity_video',
                    title='נמצא וידאו ללא VideoObject',
                    description='העמוד מכיל וידאו (לפי OpenGraph) אבל אין סכמת VideoObject.',
                    severity=Severity.HIGH,
                    category=Category.OPPORTUNITY,
                    impact='Video Rich Results / Video Carousel',
                    fix='הוסף סכמת VideoObject עם name, description, thumbnailUrl, uploadDate',
                    schema_type='VideoObject',
                    rich_result='Video Rich Results',
                    priority_score=80
                ))

        # SearchAction for WebSite
        if 'WebSite' in self.entities_by_type:
            for website in self.entities_by_type['WebSite']:
                if not website.get('potentialAction'):
                    self._add(Recommendation(
                        id='opportunity_search_action',
                        title='WebSite ללא SearchAction',
                        description='הוספת SearchAction תאפשר תיבת חיפוש בתוצאות Google.',
                        severity=Severity.MEDIUM,
                        category=Category.OPPORTUNITY,
                        impact='Sitelinks Search Box',
                        fix='הוסף potentialAction עם @type: "SearchAction" ו-target עם URL template',
                        schema_type='WebSite',
                        field='potentialAction',
                        rich_result='Sitelinks Search Box',
                        priority_score=70
                    ))

        # AggregateRating opportunities
        if 'Product' in self.entities_by_type:
            for product in self.entities_by_type['Product']:
                if not product.get('aggregateRating') and not product.get('review'):
                    self._add(Recommendation(
                        id='product_no_rating',
                        title='Product ללא דירוגים או ביקורות',
                        description='מוצרים עם דירוגים בולטים יותר בתוצאות החיפוש.',
                        severity=Severity.MEDIUM,
                        category=Category.OPPORTUNITY,
                        impact='כוכבי דירוג בתוצאות החיפוש',
                        fix='הוסף aggregateRating או review אם יש לך נתוני דירוג',
                        schema_type='Product',
                        field='aggregateRating',
                        rich_result='Star Ratings',
                        priority_score=75
                    ))

        if 'LocalBusiness' in self.entities_by_type:
            for business in self.entities_by_type['LocalBusiness']:
                if not business.get('aggregateRating'):
                    self._add(Recommendation(
                        id='business_no_rating',
                        title='LocalBusiness ללא דירוג',
                        description='עסקים מקומיים עם דירוגים מופיעים בולטים יותר ב-Maps ובחיפוש.',
                        severity=Severity.MEDIUM,
                        category=Category.OPPORTUNITY,
                        impact='כוכבים ב-Local Pack / Maps',
                        fix='הוסף aggregateRating עם ratingValue ו-ratingCount',
                        schema_type='LocalBusiness',
                        field='aggregateRating',
                        rich_result='Star Ratings in Maps',
                        priority_score=75
                    ))

    # =========================================================================
    # E-E-A-T SIGNALS
    # =========================================================================

    def _check_eeat_signals(self):
        """Check for E-E-A-T (Experience, Expertise, Authoritativeness, Trustworthiness) signals"""

        org = self.identity.get('organization')
        if org:
            # Check sameAs for authority signals
            same_as = org.get('sameAs', [])
            if isinstance(same_as, str):
                same_as = [same_as]

            found_platforms = set()
            for link in same_as:
                if isinstance(link, str):
                    for domain, info in SOCIAL_PLATFORMS.items():
                        if domain in link.lower():
                            found_platforms.add(info['name'])

            # Wikidata is gold standard for E-E-A-T
            has_wikidata = any('wikidata.org' in str(link).lower() for link in same_as)
            if not has_wikidata:
                self._add(Recommendation(
                    id='eeat_no_wikidata',
                    title='Organization ללא קישור Wikidata',
                    description='קישור ל-Wikidata הוא הסיגנל החזק ביותר לאימות זהות הארגון.',
                    severity=Severity.MEDIUM,
                    category=Category.OPPORTUNITY,
                    impact='Knowledge Panel - Wikidata הוא המקור המועדף של Google',
                    fix='צור דף Wikidata לארגון והוסף את הקישור ל-sameAs',
                    schema_type='Organization',
                    field='sameAs',
                    priority_score=80
                ))

            # Wikipedia
            has_wikipedia = any('wikipedia.org' in str(link).lower() for link in same_as)
            if not has_wikipedia and has_wikidata:
                self._add(Recommendation(
                    id='eeat_no_wikipedia',
                    title='יש Wikidata אבל אין Wikipedia',
                    description='קישור ל-Wikipedia משלים את Wikidata לאימות סמכות.',
                    severity=Severity.LOW,
                    category=Category.OPPORTUNITY,
                    impact='תמיכה נוספת ל-Knowledge Panel',
                    fix='אם יש דף Wikipedia, הוסף אותו ל-sameAs',
                    schema_type='Organization',
                    field='sameAs',
                    priority_score=50
                ))

            # LinkedIn for B2B authority
            has_linkedin = any('linkedin.com' in str(link).lower() for link in same_as)
            if not has_linkedin:
                self._add(Recommendation(
                    id='eeat_no_linkedin',
                    title='Organization ללא LinkedIn',
                    description='LinkedIn הוא פלטפורמה חשובה לאימות עסקי.',
                    severity=Severity.LOW,
                    category=Category.OPPORTUNITY,
                    impact='אימות עסקי ו-E-E-A-T',
                    fix='הוסף את דף ה-LinkedIn Company ל-sameAs',
                    schema_type='Organization',
                    field='sameAs',
                    priority_score=55
                ))

            # Social presence breadth
            if len(found_platforms) < 3:
                self._add(Recommendation(
                    id='eeat_low_social',
                    title='נוכחות חברתית מצומצמת',
                    description=f'נמצאו רק {len(found_platforms)} פלטפורמות ב-sameAs. מומלץ לפחות 3-4.',
                    severity=Severity.LOW,
                    category=Category.OPPORTUNITY,
                    impact='E-E-A-T: נוכחות רחבה מחזקת אמינות',
                    fix='הוסף קישורים לפרופילים ב-Facebook, LinkedIn, Instagram, YouTube וכו\'',
                    schema_type='Organization',
                    field='sameAs',
                    priority_score=45
                ))

            # Contact information for trust
            if not org.get('telephone') and not org.get('email'):
                self._add(Recommendation(
                    id='eeat_no_contact',
                    title='Organization ללא פרטי קשר',
                    description='פרטי קשר (טלפון, אימייל) מחזקים אמינות.',
                    severity=Severity.LOW,
                    category=Category.OPPORTUNITY,
                    impact='Trust signals - קל ליצור קשר',
                    fix='הוסף telephone או email או contactPoint',
                    schema_type='Organization',
                    field='contactPoint',
                    priority_score=50
                ))

        # Check author E-E-A-T for articles
        author = self.identity.get('author')
        if author:
            author_same_as = author.get('sameAs', [])
            if isinstance(author_same_as, str):
                author_same_as = [author_same_as]

            if len(author_same_as) == 0:
                self._add(Recommendation(
                    id='author_no_sameas',
                    title='Author ללא sameAs',
                    description='קישורים לפרופילים של המחבר מחזקים E-E-A-T.',
                    severity=Severity.MEDIUM,
                    category=Category.OPPORTUNITY,
                    impact='E-E-A-T: הוכחת מומחיות המחבר',
                    fix='הוסף sameAs עם קישורים ל-LinkedIn, Twitter, דף מחבר באתר',
                    schema_type='Person',
                    field='sameAs',
                    priority_score=65
                ))

            if not author.get('jobTitle') and not author.get('description'):
                self._add(Recommendation(
                    id='author_no_credentials',
                    title='Author ללא אישורים/תפקיד',
                    description='jobTitle או description מסבירים למה המחבר מוסמך לכתוב.',
                    severity=Severity.LOW,
                    category=Category.OPPORTUNITY,
                    impact='E-E-A-T: הוכחת מומחיות',
                    fix='הוסף jobTitle ו/או description למחבר',
                    schema_type='Person',
                    field='jobTitle',
                    priority_score=55
                ))


# =============================================================================
# MAIN ANALYSIS FUNCTION
# =============================================================================

def analyze_schemas(entities: List[Dict], url: str, opengraph: Optional[Dict] = None) -> Dict[str, Any]:
    """
    Main entry point for schema analysis.

    Args:
        entities: List of flattened JSON-LD entities
        url: Page URL
        opengraph: Optional OpenGraph data

    Returns:
        Comprehensive analysis with recommendations
    """
    engine = RecommendationEngine(entities, url, opengraph)
    return engine.analyze()
