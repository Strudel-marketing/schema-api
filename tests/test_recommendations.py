import unittest

from recommendations import RecommendationEngine


def recommendation_rows(result):
    return [row for severity_rows in result["recommendations"].values() for row in severity_rows]


def recommendation_ids(result):
    return [row["id"] for row in recommendation_rows(result)]


def recommendations_by_id(result, recommendation_id):
    return [row for row in recommendation_rows(result) if row["id"] == recommendation_id]


class RecommendationSemanticsTests(unittest.TestCase):
    def test_complementary_same_id_entities_merge_without_duplicate_warning(self):
        entities = [
            {
                "@type": ["Organization", "TravelAgency"],
                "@id": "https://example.com/#organization",
                "name": "Example Tours",
                "url": "https://example.com/",
            },
            {
                "@type": ["Organization", "TravelAgency"],
                "@id": "https://example.com/#organization",
                "logo": {"@type": "ImageObject", "url": "https://example.com/logo.png"},
                "sameAs": ["https://example.com/profile"],
            },
        ]

        engine = RecommendationEngine(entities, "https://example.com/about-us/")
        result = engine.analyze()

        self.assertNotIn("duplicate_id", recommendation_ids(result))
        self.assertEqual(1, len(engine.entities_by_type["Organization"]))
        merged = engine.entities_by_type["Organization"][0]
        self.assertEqual("Example Tours", merged["name"])
        self.assertIn("logo", merged)
        self.assertEqual(["https://example.com/profile"], merged["sameAs"])

    def test_conflicting_same_id_identity_keeps_high_warning(self):
        entities = [
            {
                "@type": "Organization",
                "@id": "https://example.com/#organization",
                "name": "Example Tours",
                "url": "https://example.com/",
            },
            {
                "@type": "Organization",
                "@id": "https://example.com/#organization",
                "name": "Different Company",
                "url": "https://different.example/",
            },
        ]

        result = RecommendationEngine(entities, "https://example.com/about-us/").analyze()
        rows = recommendations_by_id(result, "duplicate_id")

        self.assertEqual(1, len(rows))
        self.assertEqual("structural", rows[0]["category"])
        self.assertIn(rows[0], result["recommendations"]["high"])

    def test_single_organization_with_page_entities_has_no_hierarchy_warning(self):
        entities = [
            {"@type": "Organization", "@id": "https://example.com/#organization", "name": "Example"},
            {"@type": "WebSite", "@id": "https://example.com/#website", "name": "Example", "url": "https://example.com/"},
            {"@type": "WebPage", "@id": "https://example.com/page/#webpage", "name": "Page"},
            {
                "@type": "BreadcrumbList",
                "@id": "https://example.com/page/#breadcrumb",
                "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home"}],
            },
        ]

        result = RecommendationEngine(entities, "https://example.com/page/").analyze()

        self.assertNotIn("multiple_orgs_no_hierarchy", recommendation_ids(result))

    def test_gtin_and_mpn_are_not_applicable_to_product_representing_same_tour(self):
        entities = [
            {
                "@type": "Product",
                "@id": "https://example.com/product/market-tour/#product",
                "name": "Market Tour",
                "image": "https://example.com/tour.jpg",
                "description": "Guided market tour",
                "brand": {"@type": "Brand", "name": "Example Tours"},
                "offers": {"@type": "Offer", "price": "100", "priceCurrency": "ILS", "availability": "https://schema.org/InStock"},
            },
            {
                "@type": "TouristTrip",
                "@id": "https://example.com/product/market-tour/#touristtrip",
                "name": "Market Tour",
            },
        ]

        result = RecommendationEngine(entities, "https://example.com/product/market-tour/").analyze()
        ids = recommendation_ids(result)

        self.assertNotIn("missing_recommended_Product_gtin", ids)
        self.assertNotIn("missing_recommended_Product_mpn", ids)
        self.assertIn("missing_recommended_Product_sku", ids)

    def test_physical_product_keeps_gtin_and_mpn_recommendations(self):
        entities = [
            {
                "@type": "Product",
                "@id": "https://example.com/product/camera/#product",
                "name": "Camera",
                "image": "https://example.com/camera.jpg",
                "description": "Physical camera",
                "brand": {"@type": "Brand", "name": "Example"},
                "offers": {"@type": "Offer", "price": "100", "priceCurrency": "ILS", "availability": "https://schema.org/InStock"},
            }
        ]

        ids = recommendation_ids(RecommendationEngine(entities, "https://example.com/product/camera/").analyze())

        self.assertIn("missing_recommended_Product_gtin", ids)
        self.assertIn("missing_recommended_Product_mpn", ids)

    def test_unrelated_product_and_trip_on_same_page_keep_product_identifiers(self):
        entities = [
            {
                "@type": "Product",
                "@id": "https://example.com/bundle/#product",
                "name": "Physical Camera",
            },
            {
                "@type": "TouristTrip",
                "@id": "https://example.com/bundle/#touristtrip",
                "name": "Market Walking Tour",
            },
        ]

        ids = recommendation_ids(RecommendationEngine(entities, "https://example.com/bundle/").analyze())

        self.assertIn("missing_recommended_Product_gtin", ids)
        self.assertIn("missing_recommended_Product_mpn", ids)

    def test_exact_tour_name_matches_even_with_different_id_bases(self):
        entities = [
            {"@type": "Product", "@id": "https://example.com/product-a/#product", "name": "Market Tour"},
            {"@type": "TouristTrip", "@id": "https://example.com/trip-b/#trip", "name": "Market Tour"},
        ]

        ids = recommendation_ids(RecommendationEngine(entities, "https://example.com/bundle/").analyze())

        self.assertNotIn("missing_recommended_Product_gtin", ids)
        self.assertNotIn("missing_recommended_Product_mpn", ids)

    def test_hebrew_prefix_matching_does_not_strip_the_base_name(self):
        entities = [
            {"@type": "Product", "@id": "https://example.com/carmel/#product", "name": "סיור בכרמל"},
            {"@type": "TouristTrip", "@id": "https://example.com/carmel/#trip", "name": "סיור כרמל"},
        ]

        ids = recommendation_ids(RecommendationEngine(entities, "https://example.com/carmel/").analyze())

        self.assertNotIn("missing_recommended_Product_gtin", ids)
        self.assertNotIn("missing_recommended_Product_mpn", ids)

    def test_similar_generic_tour_names_with_different_destinations_do_not_match(self):
        entities = [
            {
                "@type": "Product",
                "@id": "https://example.com/bundle/#product",
                "name": "סיור קולינרי פרטי בירושלים",
            },
            {
                "@type": "TouristTrip",
                "@id": "https://example.com/bundle/#touristtrip",
                "name": "סיור קולינרי פרטי בחיפה",
            },
        ]

        ids = recommendation_ids(RecommendationEngine(entities, "https://example.com/bundle/").analyze())

        self.assertIn("missing_recommended_Product_gtin", ids)
        self.assertIn("missing_recommended_Product_mpn", ids)

    def test_near_identical_hebrew_tour_names_suppress_product_identifiers(self):
        entities = [
            {
                "@type": "Product",
                "@id": "https://example.com/product/machne-yehuda/#product",
                "name": "סיור קולינרי במחנה יהודה",
            },
            {
                "@type": "TouristTrip",
                "@id": "https://example.com/product/machne-yehuda/#touristtrip",
                "name": "סיור קולינרי בשוק מחנה יהודה",
            },
        ]

        ids = recommendation_ids(RecommendationEngine(entities, "https://example.com/product/machne-yehuda/").analyze())

        self.assertNotIn("missing_recommended_Product_gtin", ids)
        self.assertNotIn("missing_recommended_Product_mpn", ids)

    def test_itemlist_is_optional_for_content_archive_but_expected_for_ecommerce_category(self):
        breadcrumb = {
            "@type": "BreadcrumbList",
            "@id": "https://example.com/category/example/#breadcrumb",
            "itemListElement": [{"@type": "ListItem", "position": 1, "name": "Home"}],
        }
        content_entities = [
            {"@type": "CollectionPage", "@id": "https://example.com/category/articles/#page", "name": "Articles"},
            breadcrumb,
        ]
        ecommerce_entities = [
            {"@type": "CollectionPage", "@id": "https://example.com/category/cameras/#page", "name": "Cameras"},
            breadcrumb,
            {"@type": "Product", "@id": "https://example.com/product/camera/#product", "name": "Camera"},
        ]
        nested_ecommerce_entities = [
            {
                "@type": "CollectionPage",
                "@id": "https://example.com/category/nested-cameras/#page",
                "name": "Nested cameras",
                "mainEntity": [{"@type": "Product", "name": "Nested Camera"}],
            },
            breadcrumb,
        ]

        content_result = RecommendationEngine(content_entities, "https://example.com/category/articles/").analyze()
        ecommerce_result = RecommendationEngine(ecommerce_entities, "https://example.com/category/cameras/").analyze()
        nested_ecommerce_result = RecommendationEngine(
            nested_ecommerce_entities,
            "https://example.com/category/nested-cameras/",
        ).analyze()

        content_rows = recommendations_by_id(content_result, "missing_schema_ItemList")
        ecommerce_rows = recommendations_by_id(ecommerce_result, "missing_schema_ItemList")
        nested_ecommerce_rows = recommendations_by_id(nested_ecommerce_result, "missing_schema_ItemList")
        self.assertEqual(1, len(content_rows))
        self.assertIn(content_rows[0], content_result["recommendations"]["low"])
        self.assertEqual(1, len(ecommerce_rows))
        self.assertIn(ecommerce_rows[0], ecommerce_result["recommendations"]["high"])
        self.assertEqual(1, len(nested_ecommerce_rows))
        self.assertIn(nested_ecommerce_rows[0], nested_ecommerce_result["recommendations"]["high"])

    def test_content_opportunities_require_evidence_and_are_deduplicated(self):
        article = {
            "@type": "Article",
            "@id": "https://example.com/blog/guide/#article",
            "headline": "Guide",
            "image": "https://example.com/guide.jpg",
            "datePublished": "2026-01-01",
            "author": {"@type": "Person", "name": "Author"},
        }

        no_evidence = RecommendationEngine([article], "https://example.com/blog/guide/").analyze()
        with_evidence = RecommendationEngine(
            [article],
            "https://example.com/blog/guide/",
            content_signals={"faq": True, "howto": True},
        ).analyze()

        no_evidence_ids = recommendation_ids(no_evidence)
        with_evidence_rows = recommendation_rows(with_evidence)
        self.assertFalse(any(row.get("schema_type") == "FAQPage" for row in recommendation_rows(no_evidence)))
        self.assertFalse(any(row.get("schema_type") == "HowTo" for row in recommendation_rows(no_evidence)))
        self.assertNotIn("opportunity_faq", no_evidence_ids)
        self.assertNotIn("opportunity_howto", no_evidence_ids)
        self.assertEqual(1, sum(row.get("schema_type") == "FAQPage" for row in with_evidence_rows))
        self.assertEqual(1, sum(row.get("schema_type") == "HowTo" for row in with_evidence_rows))

    def test_rating_opportunity_requires_review_evidence(self):
        product = {
            "@type": "Product",
            "@id": "https://example.com/product/camera/#product",
            "name": "Camera",
            "image": "https://example.com/camera.jpg",
            "description": "Camera",
            "brand": {"@type": "Brand", "name": "Example"},
            "offers": {"@type": "Offer", "price": "100", "priceCurrency": "ILS", "availability": "https://schema.org/InStock"},
        }

        no_evidence = RecommendationEngine([product], "https://example.com/product/camera/").analyze()
        invalid_evidence = RecommendationEngine(
            [product],
            "https://example.com/product/camera/",
            content_signals={"reviews": "false"},  # type: ignore[dict-item]
        ).analyze()
        with_evidence = RecommendationEngine(
            [product],
            "https://example.com/product/camera/",
            content_signals={"reviews": True},
        ).analyze()

        self.assertNotIn("product_no_rating", recommendation_ids(no_evidence))
        self.assertNotIn("product_no_rating", recommendation_ids(invalid_evidence))
        self.assertIn("product_no_rating", recommendation_ids(with_evidence))

    def test_deduplication_does_not_hide_distinct_structural_issues(self):
        entities = [
            {"@type": "Organization", "@id": "https://example.com/#org-a", "name": "Brand A"},
            {"@type": "Organization", "@id": "https://example.com/#org-b", "name": "Brand B"},
            {"@type": "WebSite", "@id": "https://example.com/#website", "name": "Website Name", "url": "https://example.com/"},
        ]

        ids = recommendation_ids(RecommendationEngine(entities, "https://example.com/").analyze())

        self.assertIn("multiple_orgs_no_hierarchy", ids)
        self.assertIn("name_mismatch_org_website", ids)

    def test_deduplication_does_not_hide_distinct_opportunities(self):
        organization = {
            "@type": "Organization",
            "@id": "https://example.com/#organization",
            "name": "Example",
            "sameAs": ["https://facebook.com/example"],
        }

        ids = recommendation_ids(RecommendationEngine([organization], "https://example.com/").analyze())

        self.assertIn("eeat_no_wikidata", ids)
        self.assertIn("eeat_no_linkedin", ids)
        self.assertIn("eeat_low_social", ids)

    def test_deduplication_keeps_issues_for_distinct_anonymous_entities(self):
        entities = [
            {"@type": "Product"},
            {"@type": "Product"},
        ]

        result = RecommendationEngine(entities, "https://example.com/products/").analyze()

        self.assertEqual(2, len(recommendations_by_id(result, "missing_required_Product_name")))


if __name__ == "__main__":
    unittest.main()
