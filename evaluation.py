import requests


API_URL = "http://127.0.0.1:8000/ask"


test_cases = [
    {
        "question": "What is the refund timeline?",
        "expected": ["nine", "9 weeks"]
    },
    {
        "question": "What is the refund deadline?",
        "expected": ["18 November 2026"]
    },
    {
        "question": "What types of procedures are mentioned in the refund timeline?",
        "expected": ["financial", "GST", "accounting"]
    }
]

def evaluate():

    passed = 0

    print("\nRAG Evaluation\n")
    print("=" * 50)

    for i, test in enumerate(test_cases, start=1):

        response = requests.post(
            API_URL,
            json={"question": test["question"]}
        )

        if response.status_code != 200:
            print(f"\nTest {i}: FAILED")
            print("API request failed.")
            continue

        result = response.json()
        answer = result["answer"].lower()

        matched = any(
            expected.lower() in answer
            for expected in test["expected"]
        )

        if matched:
            passed += 1
            status = "PASSED"
        else:
            status = "FAILED"

        print(f"\nTest {i}: {status}")
        print(f"Question: {test['question']}")
        print(f"Answer: {result['answer']}")

        print("Sources:")
        for source in result["sources"]:
            print(
                f"  - {source['document']} "
                f"Page {source['page']} "
                f"(score={source['similarity']})"
            )

    print("\n" + "=" * 50)
    print(f"Evaluation Result: {passed}/{len(test_cases)} tests passed")


if __name__ == "__main__":
    evaluate()