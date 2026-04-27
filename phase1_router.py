# phase1_router.py

from langchain_chroma import Chroma
from langchain_core.documents import Document
from config import embeddings, BOT_PERSONAS


def build_persona_store():
    """Creates a small in-memory vector DB of bot personas."""
    
    documents = []

    for bot_id, bot in BOT_PERSONAS.items():
        documents.append(
            Document(
                page_content=bot["persona"],
                metadata={
                    "bot_id": bot_id,
                    "name": bot["name"]
                }
            )
        )

    return Chroma.from_documents(
        documents,
        embedding=embeddings,
        collection_name="persona_router"
    )


def route_post_to_bots(post: str, threshold: float = 0.85):
    """
    Match incoming post with relevant bot personas using cosine similarity.
    """

    print("\n--- PHASE 1: Persona Routing ---")
    print(f"Incoming post: {post[:80]}...\n")

    store = build_persona_store()

    # top results 
    results = store.similarity_search_with_score(post, k=5)

    matched = []

    for doc, distance in results:
    
        similarity = 1 - distance         # cosine distance base similarity

        name = doc.metadata["name"]
        bot_id = doc.metadata["bot_id"]

        print(f"{name:<20} → similarity: {similarity:.3f}")

        if similarity > threshold:
            matched.append(bot_id)

    
    matched = list(set(matched))            # Remove Duplicates

    if not matched:
        print("\nNo strong match found. Using fallback bot.\n")
        return ["general_bot"]

    print(f"\nMatched bots: {matched}\n")
    return matched