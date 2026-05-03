import json
import os
import re

class Document:
    def __init__(self, page_content, metadata):
        self.page_content = page_content
        self.metadata = metadata

class RAGService:
    def __init__(self):
        self.documents = []
        self._load_all_knowledge()

    def _load_all_knowledge(self):
        """Load and structure all knowledge bases into searchable documents."""
        print("Loading all knowledge bases...")

        # 1. Airport Knowledge
        airport_path = os.path.join("Data", "airport_knowledge.json")
        if os.path.exists(airport_path):
            with open(airport_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._parse_airport_knowledge(data)

        # 2. Food Database
        food_path = os.path.join("Data", "food_database.json")
        if os.path.exists(food_path):
            with open(food_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._parse_food_database(data)

        # 3. Security Procedures
        security_path = os.path.join("Data", "security_procedures.json")
        if os.path.exists(security_path):
            with open(security_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._parse_security_data(data)

        # 4. Shopping / Duty-Free
        shopping_path = os.path.join("Data", "shopping_database.json")
        if os.path.exists(shopping_path):
            with open(shopping_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            self._parse_shopping_data(data)

        print(f"Loaded {len(self.documents)} knowledge documents.")

    def _parse_airport_knowledge(self, data):
        """Parse airport_knowledge.json into meaningful, complete chunks."""

        # General info
        gen = data.get("general_information", {})
        if gen:
            self.documents.append(Document(
                page_content=(
                    f"Airport: {gen.get('name', 'Unknown')} (Code: {gen.get('code', 'N/A')}). "
                    f"Terminals: {', '.join(gen.get('terminals', []))}. "
                    f"WiFi: {gen.get('wifi', 'N/A')}."
                ),
                metadata={"source": "general_info", "type": "airport"}
            ))

        # Navigation and gates - combine each gate into one complete document
        for gate in data.get("real_airport_navigation_and_gates", []):
            loc = gate.get("location", "Unknown")
            coords = gate.get("coordinates", "")
            directions = gate.get("directions", "")
            self.documents.append(Document(
                page_content=f"Location: {loc}. Coordinates: {coords}. Directions: {directions}",
                metadata={"source": "navigation", "type": "gate", "location": loc}
            ))

        # Food and amenities - each amenity as a complete document
        for name, info in data.get("real_food_and_amenities", {}).items():
            amenity_type = info.get("type", "amenity")
            coords = info.get("coordinates", "")
            location = info.get("location", "")
            hours = info.get("opening_hours", "")
            desc = info.get("description", "")
            self.documents.append(Document(
                page_content=(
                    f"{name} is a {amenity_type} located at {location}. "
                    f"Coordinates: {coords}. Opening hours: {hours}. {desc}"
                ),
                metadata={"source": "amenities", "type": amenity_type, "name": name}
            ))

        # Passenger protocols
        protocols = data.get("synthetic_passenger_protocols", {})
        for key, value in protocols.items():
            readable_key = key.replace("_", " ").title()
            self.documents.append(Document(
                page_content=f"Protocol for {readable_key}: {value}",
                metadata={"source": "protocols", "type": "protocol"}
            ))

        # PNR database - each PNR as a searchable document
        for pnr_code, pnr_info in data.get("massive_pnr_database", {}).items():
            parts = [f"PNR {pnr_code}: Passenger {pnr_info.get('passenger_name', 'Unknown')}."]
            parts.append(f"Flight {pnr_info.get('flight_number', 'N/A')}.")
            parts.append(f"Status: {pnr_info.get('status', 'N/A')}.")
            parts.append(f"Gate: {pnr_info.get('gate', 'N/A')}.")
            parts.append(f"Boarding time: {pnr_info.get('boarding_time', 'N/A')}.")
            parts.append(f"Destination: {pnr_info.get('destination', 'N/A')}.")
            connecting = pnr_info.get("connecting_flight")
            if connecting:
                parts.append(
                    f"Connecting flight: {connecting.get('flight_number', 'N/A')} "
                    f"from Gate {connecting.get('gate', 'N/A')}, "
                    f"layover {connecting.get('layover_time', 'N/A')}, "
                    f"to {connecting.get('destination', 'N/A')}."
                )
            self.documents.append(Document(
                page_content=" ".join(parts),
                metadata={"source": "pnr", "type": "pnr", "pnr": pnr_code}
            ))

    def _parse_food_database(self, data):
        """Parse food_database.json into complete restaurant documents."""
        for r in data.get("restaurants", []):
            diet_tags = []
            opts = r.get("dietary_options", {})
            if opts.get("vegetarian"): diet_tags.append("Vegetarian")
            if opts.get("non_vegetarian"): diet_tags.append("Non-Vegetarian")
            if opts.get("vegan"): diet_tags.append("Vegan")
            if opts.get("jain"): diet_tags.append("Jain")

            menu_items = ", ".join(
                [f"{m['name']} (₹{m['price']})" for m in r.get("menu_highlights", [])]
            )

            gate_info = ", ".join(r.get("gate_proximity", []))

            self.documents.append(Document(
                page_content=(
                    f"Restaurant: {r.get('name', 'Unknown')}. "
                    f"Location: {r.get('terminal', 'N/A')}, {r.get('zone', 'N/A').replace('_', ' ')}. "
                    f"Near gates: {gate_info}. "
                    f"Cuisine: {', '.join(r.get('cuisine_types', []))}. "
                    f"Dietary: {', '.join(diet_tags)}. "
                    f"Rating: {r.get('rating', 'N/A')}/5. Price: {r.get('price_range', 'N/A')}. "
                    f"Wait time: {r.get('estimated_wait_time', 'N/A')}. "
                    f"Hours: {r.get('open_hours', 'N/A')}. "
                    f"Menu highlights: {menu_items}. "
                    f"Amenities: {', '.join(r.get('amenities', []))}."
                ),
                metadata={"source": "food", "type": "restaurant", "name": r.get("name")}
            ))

    def _parse_security_data(self, data):
        """Parse security_procedures.json into searchable documents."""
        for code, airport in data.get("airports", {}).items():
            name = airport.get("name", code)

            # Domestic security
            dom = airport.get("domestic_security", {})
            if dom:
                steps_text = " ".join(
                    [f"Step {s['step']}: {s['title']} - {s['description']} (~{s['time']})"
                     for s in dom.get("steps", [])]
                )
                prohibited_text = ", ".join(
                    [f"{p['item']} ({p['examples']})" for p in dom.get("prohibited_items", [])]
                )
                self.documents.append(Document(
                    page_content=(
                        f"Security at {name} ({code}) for DOMESTIC flights. "
                        f"Estimated time: {dom.get('estimated_time', 'N/A')}. "
                        f"Peak hours: {', '.join(dom.get('peak_hours', []))}. "
                        f"Steps: {steps_text}. "
                        f"Prohibited items: {prohibited_text}."
                    ),
                    metadata={"source": "security", "type": "domestic", "airport": code}
                ))

            # International security
            intl = airport.get("international_security", {})
            if intl:
                add_steps = " ".join(
                    [f"Step {s['step']}: {s['title']} - {s['description']} (~{s['time']})"
                     for s in intl.get("additional_steps", [])]
                )
                self.documents.append(Document(
                    page_content=(
                        f"Security at {name} ({code}) for INTERNATIONAL flights. "
                        f"Estimated time: {intl.get('estimated_time', 'N/A')}. "
                        f"Liquid rule: {intl.get('liquid_rule', 'N/A')}. "
                        f"Currency limit: {intl.get('currency_limit', 'N/A')}. "
                        f"Additional steps: {add_steps}."
                    ),
                    metadata={"source": "security", "type": "international", "airport": code}
                ))

        # Country warnings
        for country, warnings in data.get("country_specific_warnings", {}).items():
            warnings_text = " ".join([w["warning"] for w in warnings])
            self.documents.append(Document(
                page_content=f"Travel warnings for {country}: {warnings_text}",
                metadata={"source": "security", "type": "country_warning", "country": country}
            ))

        # Tips
        tips = data.get("tips", [])
        if tips:
            self.documents.append(Document(
                page_content=f"Security tips: {'. '.join(tips)}",
                metadata={"source": "security", "type": "tips"}
            ))

    def _parse_shopping_data(self, data):
        """Parse shopping_database.json into searchable documents."""
        for shop in data.get("shops", []):
            items_text = ", ".join(
                [f"{item['name']} (₹{item['price']}, {item.get('category', 'General')})"
                 for item in shop.get("items", [])]
            )
            offers_text = ""
            for offer in shop.get("offers", []):
                offers_text += f" Offer: {offer.get('description', '')} ({offer.get('validity', '')})."

            self.documents.append(Document(
                page_content=(
                    f"Shop: {shop.get('name', 'Unknown')}. Type: {shop.get('type', 'retail')}. "
                    f"Location: {shop.get('terminal', 'T3')}, {shop.get('zone', 'N/A').replace('_', ' ')}. "
                    f"Near gates: {', '.join(shop.get('gate_proximity', []))}. "
                    f"Opening hours: {shop.get('open_hours', 'N/A')}. "
                    f"Available items/SKUs: {items_text}. "
                    f"{offers_text}"
                ),
                metadata={"source": "shopping", "type": shop.get("type", "retail"), "name": shop.get("name")}
            ))

    def retrieve_context(self, query, k=8):
        """Retrieve the most relevant documents for a query using keyword + phrase matching."""
        if not self.documents:
            return ""

        query_lower = query.lower()
        query_words = set(re.findall(r'\w+', query_lower))
        # Remove stop words
        stop_words = {'is', 'the', 'a', 'an', 'in', 'at', 'of', 'to', 'for', 'and', 'or', 'my', 'me',
                      'where', 'what', 'how', 'can', 'i', 'do', 'does', 'are', 'there', 'this', 'that',
                      'any', 'some', 'near', 'nearby', 'find', 'show', 'tell', 'about', 'please'}
        query_words = query_words - stop_words

        if not query_words:
            return ""

        scored_docs = []
        for doc in self.documents:
            content_lower = doc.page_content.lower()
            doc_words = set(re.findall(r'\w+', content_lower))

            # Base score: word intersection
            score = len(query_words.intersection(doc_words))

            # Bonus: exact multi-word phrase match (e.g., "gate 5b")
            for word in query_words:
                if len(word) > 2 and word in content_lower:
                    score += 3

            # Bonus: if query contains a proper noun that matches document name
            if doc.metadata.get("name"):
                doc_name_lower = doc.metadata["name"].lower()
                if any(qw in doc_name_lower for qw in query_words if len(qw) > 2):
                    score += 5

            # Bonus for PNR exact match
            if doc.metadata.get("pnr"):
                pnr_lower = doc.metadata["pnr"].lower()
                if pnr_lower in query_lower:
                    score += 10

            if score > 0:
                scored_docs.append((score, doc))

        scored_docs.sort(key=lambda x: x[0], reverse=True)
        top_docs = [doc for score, doc in scored_docs[:k]]

        context = "\n\n".join([doc.page_content for doc in top_docs])
        return context

# For testing
if __name__ == "__main__":
    service = RAGService()
    print("--- Test: Where is Starbucks? ---")
    print(service.retrieve_context("Where is Starbucks?"))
    print("\n--- Test: Gate 55 ---")
    print(service.retrieve_context("Where is Gate 55?"))
    print("\n--- Test: Security ---")
    print(service.retrieve_context("What are the security procedures?"))
    print("\n--- Test: Vegetarian food ---")
    print(service.retrieve_context("vegetarian food options"))
    print(f"\nTotal documents: {len(service.documents)}")
