
# Minecraft Book Formatter

The repository contains a Python tool that helps to arranges words and sentences from a regular text in a way, to make them fit in Minecraft Book. 

## The Problem

The Minecraft book editor lets you paste text into a book until it fits on a page. If the text fits on a single page, it will be arranged between page’s lines. The problem occurs when you try to create a longer book outside of Minecraft and import it into the game using third-party mods like: 

- [Scribble](https://github.com/chrrs/scribble)
- [BookCopy](https://github.com/eclipseisoffline/bookcopy)

This tool is designed to solve the problem of arranging plain text to ensure it is importable into Minecraft.

## Usage

### Basic Usage

The tool includes various classes that help split plain text into lines and pages, making it suitable for Minecraft books. A basic usage example is provided in `main.py`.

Example of `input.txt` content:
```text
Hi  
This text represents raw string input that obviously does not fit into a single line of Minecraft Book. But with the help of the python script this text can be formatted in a way to fit. The script will split text into lines and pages keeping the paragraphs and spaces untouched.   
Let's make these sentences a new paragraph.  
       …and this paragraph starts with some spaces.   
The text arrangement logic supports §9default§r §oMinecraft§r §n§cformatting§r attributes, beside the BOLD tag. But all of them will stay in the output text.  
With the help of extra tags you can apply specific styling and arrangement to specific parts of the text. For example: {{$new_page}} This text will always start with a new page.  
{{$new_page}}The script output can be founded in §adebug§r folder
```

The corresponding output:
```text
 -------- Page 1 --------   
1: Hi  
2: This text represents  
3: raw string input that  
4: obviously does not fit  
5: into a single line  
6: of Minecraft Book.  
7: But with the help  
8: of the python script  
9: this text can be  
10: formatted in a way to  
11: fit. The script will split  
12: text into lines  
13: and pages keeping  
14: the paragraphs  
  
 -------- Page 2 --------   
1: and spaces  
2: untouched.  
3: Let's make these  
4: sentences a new  
5: paragraph.  
6:        …and this  
7: paragraph starts with  
8: some spaces.  
9: The text arrangement  
10: logic supports §9default§r  
11: §oMinecraft§r §n§cformatting§r  
12: attributes,  
13: beside the BOLD tag.  
  
 -------- Page 3 --------   
1: But all of them will  
2: stay in the output  
3: text.  
4: With the help of extra  
5: tags you can apply  
6: specific styling  
7: and arrangement  
8: to specific parts  
9: of the text.  
10: For example:  
  
 -------- Page 4 --------   
1:  This text will always  
2: start with a new page.  
  
 -------- Page 5 --------   
1: The script output  
2: can be founded  
3: in §adebug§r folder
```

### Advanced Examples

For more creative applications, you can load content from various sources on the internet and use it to fill up book templates. Examples of such usage can be found in the following scripts:
- `che_book_writer.py`: Loads content from Telegram channels to generate importable Minecraft books.
- `joke_b_book_writer.py`: Another example of creating Minecraft books with content from Telegram.
- `neural_horo_book_writer.py`: Uses neural network-generated content for Minecraft books.
- `statham_book_writer.py`: The last example of creating Minecraft books with content from Telegram.
