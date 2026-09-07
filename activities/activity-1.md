---
title: "Activity 1: Publishing Markdown"
subtitle: "Craft of Computing"
date: "Sep 07, 2026"
---

## Task A: Setup

1. create a directory `activity-1`
2. use `wget` to download your group presentation pdf from <https://coc.apucomputing.in/~anand/group-presentations/>
3. Extract the first page of the pdf as png image

### Instructions

These are the commands that you need to run to download the pdf and extract the image. Please fix the URL of the presentation. You can find the list of all group presentation pdfs at <https://coc.apucomputing.in/~anand/group-presentations/>.

**Step 1**

Create `activity-1` directory.

```bash
$ cd
$ mkdir activity-1
$ cd activity-1
```

**Step 2**

Make sure you are in `activity-1` directory. 

```bash
$ pwd
/home/anand/activity-1
```

Download your presentation. You need to fix the URL of the presentation. The list of all group presentation pdfs is available at <https://coc.apucomputing.in/~anand/group-presentations/>.

```bash
$ wget -O group-presentation.pdf https://coc.apucomputing.in/~anand/group-presentations/Group-x-title.pdf
```

Make sure your presentation is downloaded.

```bash
$ ls
group-presentation.pdf
```

Extract the first page of the pdf using `pdftoppm`.

```bash
$ pdftoppm -png -f 1 -l 1 group-presentation.pdf slide

$ ls
group-presentation.pdf 
slide-01.png
```

it creates a new file slide-01.png. 

We used the option `-png` to ask the tool to generate a png image and the options `-f 1` and `-l 1` to indicate the page number of the first page and the last page to convert.

We could rename the file if needed.

## Task B: Practice Markdown

Create a file `markdown.md` and practice the examples from the [Markdown Tutorial][1].

Your markdown file should have:

1. Title as "Markdown"
2. One section for each section of the tutorial with the markdown examples.
3. In the `Links` section, add the following two links:
    * link to your website on `https://coc.apucomputing.in/`
    * link to slides from your group presentation 
4. In the `Images` section, show the first page of your presentation pdf, generated in task A.

[1]: https://craft-of-computing.anandology.com/2026/markdown/tutorial.html

After you are done with all sections, use the instructions in [Markdown Tools][2] to convert the markdown.md into html and pdf.

[2]: https://craft-of-computing.anandology.com/2026/markdown/tools.html

## Task C: Reflection

Write markdown page `reflection.md` with the following:
- Your impression of markdown and how you could use it in the future 
- All the commands you used to generate html and pdf
- difficulties faced in doing this activity, if any

Please use an appropriate title for the file and use sections as as needed.

Generate html and pdf for this markdown file as well.

## Task C:  Copy to server

Copy the `activity-1` directory to your `public_html` directory on the server.

First go to your home directory and verify you have activity-1 directory.

```session
$ cd
$ ls -F | grep activity
activity-1/
```

Copy the entire directory to the server.

```session
$ scp -r activity-1 coc.apucomputing.in:public_html/
```

After this you should be able to see the html file at:
`https://coc.apucomputing.in/~your-user-name/activity-1/markdown.html`.

## Task D: Create a zip file and submit

Create a zip file of entire activity-1 directory.

```session
$ cd
$ zip -r activity-1.zip activity-1
$ ls *.zip
activity-1.zip
```

Ensure the zip file has all the files needed.

```session
$ unzip -l activity-1.zip
Archive:  activity-1.zip
  Length      Date    Time    Name
---------  ---------- -----   ----
        0  2026-09-07 07:47   activity-1/
        0  2026-09-07 07:47   activity-1/markdown.html
        0  2026-09-07 07:47   activity-1/markdown.md
        0  2026-09-07 07:47   activity-1/markdown.pdf
        0  2026-09-07 07:47   activity-1/reflection.html
        0  2026-09-07 07:47   activity-1/reflection.md
        0  2026-09-07 07:47   activity-1/reflection.pdf
---------                     -------
        0                     7 files
```

The length will be different when you run it and it will be the size of each file.

Submit this zip file on moodle.
