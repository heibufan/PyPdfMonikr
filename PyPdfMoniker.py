# PDF Renamer package development in python

###################################################################################
#
#                            NOTES / LOGBOOK
#
###################################################################################

# note [September 21th, 2018]: The goal is to collect meta-data from multuple sources [PyPDF2.getDocumentInfo, PyPDF2.content headers. PyPDF2.content.page_one, google search] and then compare and treat overlapping md as valid fields.
# # _____________________:  That's the best way to get robust md for renaming pdf

###################################################################################
#
#                           DEVELOMENT UPDATED
#
###################################################################################

# September 21th, 2018: Retrieving PDF Meta-Data using PyPDF2.getDocumentInfo method
# __________________: {beta-done} code retrieve Author, Title, Year, Doi
# __________________: {*next} need to write regular expression code to get YEAR
# __________________: {*next} YEAR can also be in ModDate
# __________________: {*next} YEAR retrieved in CreationDate seems to be 1 year before actual pubication year, capturing date received or published online.
# __________________: {*next} need to retrieve Keywords from md as well if present


# September 22th, 2018: {*cur} Start writing code to retrieve PDF Meta-Data using PyPDF2 content method. Getting patterns in top/bottom of pages where we can find informations such as Author, Journal Name, Article Title
# __________________: see def pdf_content_meta_data_header / footer (pdf_toread, pages_num):
# __________________: current version doesnt store headers' meta-data in a master list, it simply print the md so retrieved.
# __________________: {*next} Page 1 non-duplicate or duplicate might be the Article Title or Journal Article, or both
# __________________: {*next} Parsing First Page. Key to parsing is "\n." Structure of Short Sentence as split point

# September 25th, 2018: Testing pdf_content_meta_data_header / footer code to improve cur code only parsing the first / last 200 caracters. Not a very accurate and flexible method of capturing md.
# ____________________: Add pdf_content_page_one(pdf_toread, pages_num, title) to parse from content the equivalent md (author.s, title, year, etc.)
# ____________________: current version of function compare pdf md title field wit pdf page 1 first string and compare the matching ratio.
# ____________________: It's a good way to check title validity, but need more vetting to check if page 1 first string is a title
# ____________________: {*next} checking with [regular expression] if number and year in page 1 first string as in a lot of case it will be the Journal Name and related informations. e.g. Research Policy 41 (2012) 251– 261
# ____________________: which is a good thing, since if we find number in first string we can retrive that data: Journal Name, Year, Issue, Pages.
# ____________________: {*next} check if DOI is in first page. e.g. http://dx.doi.org/10.1787/9789264094611. Easy structure to match and parse once we know all the possible declinations.
# ____________________: {*next} for checking for patterned header/footer md, it might be better to use match_ratio = SequenceMatcher().ratio() as the current item in list is a 100% match
# ____________________: and since we have page number in header/footer, it doesnt match 100%. So one way is to use the SequenceMatcher()
# ____________________: another way is to develop a more robust regular expression to catch all number structure from header / footer.
# ____________________: {*next} pdf md: parse '/Subject': 'Urban Studies 2014.51:2219-2234'.
# Test
import os
import PyPDF2
from pprint import pprint
from difflib import SequenceMatcher # check matching ratio of two strings

#def date_format(year_string_raw):

def pdf_content_page_one(pdf_toread, pages_num, title):

    # chunk of code for testing purpose only. It grab and print pdf page 1
    # Grab very first line of text of page 1 as it might consistently/potentially be article title

    # have a crack at page 0 first
    page_content = pdf_toread.getPage(0)
    neirong = page_content.extractText()
    #neirong_start = neirong[0:500]
    pprint('neirong_start_first_200:' + neirong)
    neirong_split = neirong.split('\n')
    pprint(neirong_split)

    # compare string retrieved in title md with first chunk of page 1 to see if match
    if title != 'Title':
        first_chunk_page_one = neirong_split[0]
        # de-capitalized both string
        first_chunk_page_one = first_chunk_page_one.lower()
        title = title.lower()
        # check if space between words in title string
        first_chunk_page_one = first_chunk_page_one.replace(' ', '')
        title = title.replace(' ', '')
        print(first_chunk_page_one)
        print(title)

        match_ratio = SequenceMatcher(None, title, first_chunk_page_one).ratio()
        print(str(match_ratio))

def pdf_content_meta_data_header(pdf_toread, pages_num, title):
    pprint('###################################### in pdf_content_meta_data_header function##########################' )
# function retrieve meta-data, not with the PyPDF2.getDocumentInfo method, but by retrieving patterned data in the pdf content itself.
# md is short for meta-data
# neirong is chinese word for content


    # first call function parsing pdf first page data
    pdf_content_page_one(pdf_toread, pages_num, title)

    # list that store raw page_header md
    pages_header = []

    for i in range(0, pages_num):
        page_content = pdf_toread.getPage(i)
        neirong = page_content.extractText()
        neirong_start = neirong[0:200]
        neirong_first_chunk = neirong_start.split('\n')
        neirong_first_string = neirong_first_chunk[0]
        pages_header.append(neirong_first_string)

    pprint('page_header:' + str(pages_header))
    # find all strings that have duplicate, and store then orderly in a list or dict
    # then do the same for all non-duplicated strings

    pages_header_md = []
    page_header_no_dup = []
    for item in pages_header:
        pprint('in item in page_header loop: ' + item)

        count_duplicate = pages_header.count(item)
        pprint('count: ' + str(count_duplicate))

        if count_duplicate >1:
            # add to new list
            if item not in pages_header_md:
                pages_header_md.append(item)

        elif count_duplicate == 1:
            page_header_no_dup.append(item)

        else:
            continue

    pprint('md:' + str(pages_header_md))
    pprint('no_dup:' + str(page_header_no_dup))

    if len(pages_header_md) == 0:
        # it's possible that header's md is stocked at the end of each pdf page content
        pdf_content_meta_data_footer(pdf_toread, pages_num)

    # false positive duplicate items
    # JSTOR-Protected Pattern
    # This content downloaded
    # UTCAll use subject to http://about.jstor.org/terms'


def pdf_content_meta_data_footer(pdf_toread, pages_num):
    pprint('###################################### in pdf_content_meta_data_footer function##########################' )
# function retrieve meta-data, not with the PyPDF2.getDocumentInfo method, but by retrieving patterned data in the pdf content itself.
# md is short for meta-data
# neirong is chinese word for content

    pages_footer = []
    # have a crack at page 0 first
    page_content = pdf_toread.getPage(0)
    neirong = page_content.extractText()
    neirong_end = neirong[-200:]
    pprint('neirong_end:' + neirong_end)


    for i in range(0, pages_num):
        page_content = pdf_toread.getPage(i)
        neirong = page_content.extractText()
        neirong_end = neirong[-200:]
        neirong_end_chunk = neirong_end.split('\n')

        # grab last chunk
        neirong_last_chunk = neirong_end_chunk[-1:]
        # grab string in list
        neirong_last_string = neirong_last_chunk[0]
        # check if numeric
        if neirong_last_string.isnumeric() is True:
            # need to grab the one before
            neirong_last_chunk = neirong_end_chunk[-2:]
            neirong_last_string = neirong_last_chunk[0]

        # if False it means we already have the first string
        # check if any number in string as it is most likely page number

        num_there(neirong_last_string)

        if True:
            # need to remove page number
            neirong_last_string = ''.join([i for i in neirong_last_string if not i.isdigit()])

        # add string to list
        pages_footer.append(neirong_last_string)

    pprint('pages_footer:' + str(pages_footer))
    # find all strings that have duplicate, and store then orderly in a list or dict
    # then do the same for all non-duplicated strings

    pages_footer_md = []
    page_footer_no_dup = []
    for item in pages_footer:
        pprint('in item in page_footer loop: ' + item)

        count_duplicate = pages_footer.count(item)
        pprint('count: ' + str(count_duplicate))

        if count_duplicate >1:
            # add to new list
            if item not in pages_footer_md:
                pages_footer_md.append(item)

        elif count_duplicate == 1:
            page_footer_no_dup.append(item)

        else:
            continue

    pprint('md:' + str(pages_footer_md))
    pprint('no_dup:' + str(page_footer_no_dup))

def num_there(s):

    return any(i.isdigit() for i in s)
########################################################################################################################


#                                                           START OF PROGRAM


########################################################################################################################
# Lists, Dicts, and Counters

new_title_list = []
count_pdf = 0
doi_list = []

# Objective 1

# in PyPDF2, extracting meta-data use getDocumentInfo method from info class. The following attributes can be called:

#author
#creator
#producer
#subject
#title

path = "C:\\Users\\cinep\\Desktop\\Lanbufan-Razer\\1_ACADEMIC-LIFE\\1_UBC-PhD-PROGRAM_2014-2019 (m)\\3_DOCTORAL-DISSERTATION (M)\\13_PHD-DISS (current-master-Mendeley)"

files =  os.listdir(path)
pprint(files)

for file in files:
    #print(file)
    # Rename only pdf files
    try:
        #fullName = os.path.join(path, fileName)
        #if (not os.path.isfile(fullName) or fileName[-4:] != '.pdf'):
        if file[-4:] == '.pdf':

            count_pdf = count_pdf + 1
            flag_doi = 0
            doi_item = []

            # We have a PDF file to check

            print('which file come here?')
            print(file)
            # reinitialize list where the new informations that will make the new title will be temp. store
            file_new_title_list = []
            # Grab file full address not for parsing reasons, but to open the doc with PyPDF2
            file_location = os.path.join(path, file)
            print('file_location: ' + file_location)

            #valid_file = fullName

            #article_string_list = fileName.split('\\')
            #count_grab = len(article_string_list) - 1
            #article_title_string = article_string_list[count_grab]

            # read PDF file using file_location

            pdf_toread = PyPDF2.PdfFileReader(file_location, 'r')

            # grab PDF meta-data
            info = pdf_toread.getDocumentInfo()
            pprint(info)

            # store meta-data for author and title
            try:
                author = info.author
                print('author: ' + author)

                if author == None:
                    author = 'Author_Name'

                elif (author  == '' or author  == ' '):
                    author = 'Author_Name'

                else:
                    pass

            except:
                author = 'Author_Name'

            #if author_type == 'NoneType':
            #    author = ''
            #    print(author)

            try:
                title = info.title
                print('title: ' + title)

                # Checking if doi in title, or in lieu of title

                if (title[0:3] == 'doi' or 'doi' in title):
                    doi = title
                    flag_doi = 1


                #/Title': 'doi:10.1016/j.socnet.2004.11.008'
                #/Subject': 'Journal of Informetrics, 11 (2017) 176-197. doi:10.1016/j.joi.2016.12.005'

            # title: Morano-Foadi(revised).p65
            # As the above example, it is possible that the author name will be in the title.
            # One way to control for that false positive is to read the PDF page where the abstract is and look before where the abstract is to see if what is in title variable is actually the name.

                if title == None:
                    title = 'Title'

                elif (title  == '' or title == ' '):
                    title = 'Title'

                elif flag_doi == 1:
                    title = 'Title'

                else:
                    pass

            except:
                title = 'Title'

            # retrieve YEAR
            try:

                # CreationDate not valid
                # Switch to ModDate
                #year_string_raw = pdf_toread.documentInfo["/CreationDate"]
                year_string_raw = pdf_toread.documentInfo["/ModDate"]
                print(year_string_raw)

                #date_format(year_string_raw)

                # store meta-data for year
                year = year_string_raw[2:6]
                print('year: ' + year)

                if year == None:
                    year = 'Year'

            except:
                year = 'Year'

            # retrieve no.page to control for document type
            pages_num = pdf_toread.numPages

            # Determine Document Type.
            # note: eventually we will use ML to predict document type based on pages_num

            # for now, using pretty crude cut-off
            if pages_num <= 50:
                doc_type = 'XA'

            else:
                doc_type = 'XB'

            print('doc_type: ' + doc_type)

            # add meta-date in order to list

            file_new_title_list.append(doc_type)
            file_new_title_list.append(year)
            file_new_title_list.append(author)
            file_new_title_list.append(title)

            print(file_new_title_list)

            pdf_new_title = '_'
            pdf_new_title = pdf_new_title.join(file_new_title_list)
            #print(pdf_new_title)

            # Cleaning new title

            pdf_new_title = pdf_new_title.replace(' ', '-')
            pdf_new_title = pdf_new_title.replace('/', '')
            pdf_new_title = pdf_new_title.replace('\\', '')
            pdf_new_title = pdf_new_title.replace(' ', '')
            pdf_new_title = pdf_new_title.replace('.', '')
            pdf_new_title = pdf_new_title.replace(':', '')
            pdf_new_title = pdf_new_title.replace(';', '')
            pdf_new_title = pdf_new_title.replace('"', '')
            pdf_new_title = pdf_new_title.replace(',', '')

            #(
           # )

            # add .pdf extension

            pdf_new_title = pdf_new_title + '.pdf'

            print(file)
            print(pdf_new_title)

           # Checking if there is already a document with the same name

            if pdf_new_title in new_title_list:
                pdf_new_title  = pdf_new_title.replace('.pdf', '')
                pdf_new_title  = pdf_new_title + '_' + str(count_pdf)
                pdf_new_title = pdf_new_title + '.pdf'


            if len(pdf_new_title) >=99:
                pdf_new_title = pdf_new_title[0:99] + '.pdf'

            # Renaming pdf document

            os.rename(os.path.join(path, file), os.path.join(path, pdf_new_title))

            new_title_list.append(pdf_new_title)

            # making sure
            #file = file.replace('.pdf', '')
            #os.rename(os.path.join(path, file), os.path.join(path, pdf_new_title))

            print('title was renamed')
            print('\n')

            # Retrieving DOI

            try:

                doi = pdf_toread.documentInfo["/doi"]
                flag_doi = 1

            except:

                if flag_doi == 0:

                    try:
                        subject = info.subject

                        if (subject[0:3] == 'doi' or 'doi' in subject):
                            doi = subject
                            flag_doi = 1

                    except:
                        pass

            if flag_doi == 1:

                doi_item = [pdf_new_title, doi]
                doi_list.append(doi_item)

    except:
        pass

pprint(doi_list)

pdf_content_meta_data_header(pdf_toread, pages_num, title)
