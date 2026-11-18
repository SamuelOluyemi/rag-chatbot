
from app.services.generation_service import generate_answer


def test_answer_generation():
    query = "What is Retrieval-Augmented Generation?"

    context = [
        (
            "Retrieval-Augmented Generation (RAG) is a technique "
            "that combines information retrieval with generative "
            "AI. It retrieves relevant information from external "
            "documents and uses that information to generate "
            "context-aware answers."
        )
    ]

    print("Question:", query)
    print("\nGenerating answer using Ollama...\n")

    answer = generate_answer(
        query=query,
        context=context,
    )

    print("Generated answer:")
    print(answer)

    print("\nAnswer generation test completed!")


if __name__ == "__main__":
    test_answer_generation()

