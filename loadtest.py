from loader import Loader

urls = [
    'http://example.com',
    'http://example.org',
    'http://example.net',
]


def main():
    loader = Loader()
    for url in urls:
        for i in range(50):
            loader.load_url(url)

    loader.wait_to_finish()

    print("\nLoad times:")
    for url, load_time in loader.load_times.items():
        print(f"{url}: {[int(t*1000) for t in load_time]} ms")


if __name__ == "__main__":
    main()
