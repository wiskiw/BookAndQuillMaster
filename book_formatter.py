from text_container import McBook


class McBookFormatter:

    def __init__(self, book: McBook):
        self.__book = book

    def to_json(self) -> dict:
        book_json = {}

        # write book title
        title = self.__book.get_title()
        if title is not None:
            book_json['title'] = title

        # write book content
        page_str_list = []
        for page in self.__book.get_pages():

            line_str_list = []
            for line in page.get_lines():
                line_str_list.append(line.get_text())

            page_str_list.append(line_str_list)

        book_json['pages'] = page_str_list

        return book_json

    def to_pretty_text(self) -> str:
        book_str_list = []

        # write book title
        title = self.__book.get_title()
        if title is not None:
            book_str_list.append(f"title: {title}")

        # write book content
        page_str_list = []
        for enumerated_page in enumerate(self.__book.get_pages()):
            index = enumerated_page[0]
            page = enumerated_page[1]
            page_number = index + 1

            line_str_list = []
            for enumerated_line in enumerate(page.get_lines()):
                index = enumerated_line[0]
                line = enumerated_line[1]
                line_number = index + 1

                line_str_list.append(f"{line_number}: {line.get_text()}")

            page_str = '\n'.join(line_str_list)
            page_str_list.append(f" -------- Page {page_number} -------- \n" + page_str)
        book_str_list.append('\n\n'.join(page_str_list))

        return '\n'.join(book_str_list)
