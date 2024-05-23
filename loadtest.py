from loader import Loader


def main():
    loader = Loader("http://example.com")
    loader.start()

    print("\nLoad times:")
    for lr in loader.loader_requests:
        print(int((lr.end_time - lr.start_time)*1000), lr.end_time, lr.status)


if __name__ == "__main__":
    main()
