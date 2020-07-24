from staticjinja import Site
import os,json
from shutil import rmtree
from PIL import Image
import requests
from io import BytesIO
from urllib.parse import urlparse


def cacheDownloadAndRelinkImages(data):
    for index, link in enumerate(data["links"]):
        # parse icon name with and without extensions
        icon_url = link["iconUrl"]
        parser = urlparse(icon_url)
        icon_name_w_extension = os.path.basename(parser.path)
        icon_name_wo_extension = os.path.splitext(icon_name_w_extension)[0]
        # could also use new webp or other next gen formats
        # but webP not supported in safari
        icon_name_new_extension = icon_name_wo_extension + '.png'
        webLink = '/static/' + icon_name_new_extension

        # create dist folder if new and construct path
        static_path = 'dist/static/'
        if not os.path.exists(static_path):
            os.makedirs(static_path)
        path = static_path + icon_name_new_extension

        # get and cache iconImages or relink if existing
        if os.path.exists(path):
            data["links"][index]["iconUrl"] = webLink
        else:
            response = requests.get(icon_url)
            if response and response.ok:
                img = Image.open(BytesIO(response.content))
                # TODO maybe resize small and and square sometime later?
                img.save(path)
                data["links"][index]["iconUrl"] = webLink
    return data

def renderSubjectPages():
    # renders pages for all subjects
    path_to_subject_jsons = './subjects/'

    subjectLinks = []
    for file_name in [file for file in os.listdir(path_to_subject_jsons) if file.endswith('.json')]:
        subject = file_name.replace('.json', '')

        with open(path_to_subject_jsons + file_name, encoding='utf-8') as json_file:
            data = json.load(json_file)

            # download all linked images and chang links to them to use cached local ones
            data = cacheDownloadAndRelinkImages(data)

            title = data["title"]
            subjectLinks.append({
                    "name": title,
                    "href": "/" + subject + "/"
            })

            site = Site.make_site(
                searchpath="./templates/subjects",
                outpath="dist/" + subject,
                env_globals=data)
            site.render()
    return subjectLinks

def renderHomepage(subjectLinks):
    # homepage site to copy static files
    # and link to all subjects
    site = Site.make_site(
        searchpath="./templates/main",
        outpath="dist/",
        staticpaths=["static/"],
        env_globals={
            "title": "Hauptseite",
            "links": subjectLinks
        })
    site.render()

def createCoursesJson(subjectLinks):
    courseJsonPath = 'dist/courses.json'
    # write json file for dropdown of courses links in wuex extension
    with open(courseJsonPath, 'w', encoding='utf-8') as outfile:
        json.dump(subjectLinks, outfile)


if __name__ == "__main__":
    # clear dir folder and ignore errors if no dir folder exists
    rmtree('./dir/', True)

    subjectLinks = renderSubjectPages()
    renderHomepage(subjectLinks)
    createCoursesJson(subjectLinks)
