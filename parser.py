import argparse


def create_parser():
    parser = argparse.ArgumentParser(description='Process some integers.')
    parser.add_argument('--k', metavar='key-search', type=str, nargs=1,
                        help='specify key search')
    parser.add_argument('--c', metavar='color', type=str, nargs=1,
                        help='specify search color', default="colorized")
    parser.add_argument('--o', metavar='output-dir', type=str, nargs=1,
                        help='specify key search', default="./photos/")
    parser.add_argument('--s', metavar='shape', type=str, nargs=1,
                        help='specify shape', default=None)
    parser.add_argument('--l', metavar='limit', type=int, nargs=1,
                        help='max number of images to download')
    parser.add_argument('--sim_search', metavar='similar_search', type=bool, nargs=1,
                        help='specify if you want to make a reasearch by similarity', default=False)
    parser.add_argument('--sim_search_link', metavar='similar_search_link', type=str, nargs=1,
                        help='specify the link to start the reasearch by similarity', default=None)
    return parser



if __name__ == '__main__':
    args = create_parser().parse_args()
    print(args)