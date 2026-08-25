from app.rag.retriever import get_retriever


def run_query(query):
    print("\n" + "=" * 80)
    print("QUERY:")
    print(query)
    print("=" * 80)

    retriever = get_retriever()

    docs = retriever.invoke(query)

    print(f"\nRETRIEVED DOCUMENTS: {len(docs)}\n")

    for i, doc in enumerate(docs, start=1):
        print("-" * 80)

        print(f"RESULT #{i}")

        print("SOURCE:", doc.metadata.get("source_file"))
        print("TITLE:", doc.metadata.get("title"))
        print("STATUS:", doc.metadata.get("status"))
        print("AUTHORITY:", doc.metadata.get("policy_authority"))

        print("\nCONTENT:")
        print(doc.page_content[:800])


if __name__ == "__main__":

    run_query(
        "How long does a regular customer have to return an unused backpack?"
    )

    run_query(
        "My TrailPlus membership was active when I ordered. What is my return window?"
    )

    run_query(
        "Can I put the entire Breeze Tumbler in the dishwasher?"
    )

    run_query(
        "Can you ship an Atlas Weekender to Germany?"
    )



# from app.rag.retriever import get_retriever


# def test_query(query):
#     print("\n" + "=" * 80)
#     print("QUERY:")
#     print(query)
#     print("=" * 80)

#     retriever = get_retriever()

#     docs = retriever.invoke(query)

#     print(f"\nRETRIEVED DOCUMENTS: {len(docs)}\n")

#     for i, doc in enumerate(docs, start=1):
#         print("-" * 80)

#         print(f"RESULT #{i}")

#         print("SOURCE:", doc.metadata.get("source_file"))
#         print("TITLE:", doc.metadata.get("title"))
#         print("STATUS:", doc.metadata.get("status"))
#         print("AUTHORITY:", doc.metadata.get("policy_authority"))

#         print("\nCONTENT:")
#         print(doc.page_content[:800])


# if __name__ == "__main__":

#     test_query(
#         "How long does a regular customer have to return an unused backpack?"
#     )

#     test_query(
#         "My TrailPlus membership was active when I ordered. What is my return window?"
#     )

#     test_query(
#         "Can I put the entire Breeze Tumbler in the dishwasher?"
#     )

#     test_query(
#         "Can you ship an Atlas Weekender to Germany?"
#     )