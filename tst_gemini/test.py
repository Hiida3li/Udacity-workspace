import os
from dotenv import load_dotenv
from pymilvus import MilvusClient

load_dotenv()

def connect_to_milvus():
    """Connect to Milvus database."""

    milvus_uri = os.getenv("MILVUS_URI")
    token = os.getenv("MILVUS_TOKENS")

    if not milvus_uri or not token:
        raise ValueError("MILVUS_URI or MILVUS_TOKENS not set in .env")

    milvus_client = MilvusClient(uri=milvus_uri, token=token)

    return milvus_client


class ProductSupportAgent:
    """
    AI agent that handles customer queries using the Gemini-2.5-Flash model.

    This agent intelligently processes requests to either:
    - Search the Milvus database for relevant products using hybrid (text/image) search.
    - Answer frequently asked questions based on predefined knowledge or model output.
    """


    def __init__(self):
        self.milvus_client = connect_to_milvus()
        self.system_prompt = """
        You are a helpful customer support agent for an e-commerce platform.
        Your task is to help customers find products they're looking for.

        When a customer asks about a product:
        1. Extract the key product information from their query
        2. Identify any specific requirements they mentioned (like price range, color, size, brand, etc.)
        3. Be friendly and professional in your responses

        DO NOT make up information about products you don't know about.
        Always respond based on the information you have.
        """

    def extract_search_parameters(self, customer_query: str) -> Dict[str, Any]:
        """
        Use GPT-4o-mini to extract search text and filters from customer query.

        Returns:\\
            Dict containing:
            - text_embedding_content: String to be embedded (title + tags + description)
            - filters: Dict of category, price range, and other attributes
        """
        messages = [
            {"role": "system", "content": """
            Extract product search parameters from the customer query.

            Return a JSON object with these fields:
            1. "text": A string combining the key product terms the customer is looking for.
               This should include product type, features, and any descriptive terms. This will be used
               to search product titles, tags, and descriptions.
            2. "filters": A dictionary of filter parameters including:
               - "category": Product category if specified from the list in <<CATEGORIES>> section below
               - "price_range": An object with "min" and "max" if price range is mentioned. use the below <<PRICING_RULES>> to handle each case
               - "attributes": A dictionary of attributes mentioned in the <<ATTRIBUTES>> section below. 

            Only include filters that are explicitly mentioned in the query. If for example the category is not mentioned don't even include it as a key to the response.

            CATEGORIES:            
            ['Desks', 'Desks / Components', 'Desks / Office Desks', 'Furnitures / Chairs', 'Desks / Gaming Desks', 'Furnitures / Couches', 'Desks / Glass Desks', 'Desks / Standing Desks', 'Desks / Foldable Desks', 'Furnitures', 'Furnitures / Sofas', 'Furnitures / Recliners', 'Furnitures / Beds', 'Furnitures / Wardrobes', 'Boxes', 'Boxes / Vintage Boxes', 'Boxes / Rustic Boxes', 'Boxes / Luxury Boxes', 'Boxes / Stackable Boxes', 'Boxes / Collapsible Boxes', 'Drawers', 'Drawers / Nightstand Drawers', 'Drawers / Under-bed Drawers', 'Drawers / File Drawers', 'Drawers / Kitchen Drawer Units', 'Cabinets', 'Cabinets / Kitchen Cabinets', 'Cabinets / Bathroom Cabinets', 'Cabinets / Storage Cabinets', 'Cabinets / Medicine Cabinets', 'Bins', 'Bins / Laundry Bins', 'Bins / Toy Bins', 'Bins / Food Storage Bins', 'Lamps', 'Lamps / Desk Lamps', 'Lamps / Ceiling Lamps', 'Lamps / Chandeliers', 'Lamps / Touch Lamps', 'Services / Design and Planning', 'Services', 'Services / Delivery and Installation', 'Services / Repair and Maintenance', 'Services / Relocation and Moving', 'Multimedia', 'Multimedia / Virtual Design Tools', 'Multimedia / Augmented Reality Tools', 'Multimedia / Education Tools', 'giftcard', 'snowboard', 'accessories']
             PRICING_RULES:
             1- if a range is mentioned then return: {"min": MIN, "max": MAX, "operation": "range"} 
             2- If the customer asks for products LOWER than or EQUAL: {"min": null, "max": MAX, "operation": "loe"} 
             3- If the customer asks for products HIGHER than or EQUAL: {"min": MIN, "max": null, "operation": "hoe"} 
             4- If the customwer asks for EXACT price: {"min": PRICE, "max": null, "operation": "eq"} 

            ATTRIBUTES:
            1- color: [white, black]
            2- size_: [s, m, l]
             Example:
             {
                "text": "Summer T-shirt A men's t-shirt made from cotton that can be washed in the washer.",
                "filters": {
                               "category": "Men",
                               "price_range": {"min": PRICE, "max": PRICE, "operation": "eq"} 
                               "attributes" {"color": "white", "size_": "s"}
                            }
             }
            """},
            {"role": "user", "content": customer_query}
        ]

        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            response_format={"type": "json_object"}
        )

        # Parse the returned JSON
        try:
            search_params = json.loads(response.choices[0].message.content)
            print("============================================")
            print(search_params)
            print("============================================")
            return search_params
        except json.JSONDecodeError:
            # Fallback to basic extraction if JSON parsing fails
            return {
                "text_embedding_content": customer_query,
                "filters": {}
            }