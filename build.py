# -*- coding: utf-8 -*-

from staticjinja import Site
import os,json
from shutil import rmtree, move

from PIL import Image
import requests
from io import BytesIO
from urllib.parse import urlparse
import favicon
from base64 import b64encode


def createManifest(subjectPath = None, subjectTitle = None, color = None, background_color = None, toBasePath = '.'):
    data = {
        "name": "Wuel Quick Links",
        "short_name": "Wuel",
        "description": "Quick links for students at the university würzburg to save you time",
        "theme_color": "#fff4f4",
        "background_color": "#004188",
        "display": "minimal-ui",
        "orientation": "portrait",
        "scope": "/",
        "start_url": "/",
        "icons": [
            {
                "src":  toBasePath + "/static/icons/maskable_icon_x48.png",
                "sizes": "48x48",
                "type": "image/png",
                "purpose": "any maskable"
            },
                        {
                "src":  toBasePath + "/static/icons/maskable_icon_x72.png",
                "sizes": "72x72",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src":  toBasePath + "/static/icons/maskable_icon_x128.png",
                "sizes": "128x128",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src":  toBasePath + "/static/icons/maskable_icon_x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable"
            },
            {
                "src":  toBasePath + "/static/icons/maskable_icon_x512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable"
            }
        ]
    }
    if subjectPath and subjectTitle and color and background_color:
        data["name"] = "Wuel - " + subjectTitle + " Links"
        data["short_name"] = "Wuel - " + subjectPath
        data["description"] = "Quick links for " + subjectTitle + " students at the university würzburg to save you time"
        data["theme_color"] = color
        data["background_color"] = background_color
        data["start_url"] = "/" + subjectPath + "/"
        data["scope"] = "/" + subjectPath + "/"
    
    base_path = "dist/"
    filename = "manifest.json"
    if subjectPath:
        path = base_path + subjectPath + "/" + filename
        print("Creating manifest.json for " + subjectPath + "...")
    else:
        path = base_path + filename
        print("Creating manifest.json for index...")

    # write json file for web manifest
    with open(path, 'w', encoding='utf-8') as outfile:
        json.dump(data, outfile, ensure_ascii=False)


iconsDownloadedUrls = []
def cacheDownloadAndRelinkImages(data):
    for index, link in enumerate(data["links"]):
        # parse icon name with and without extensions
        try:
            icon_url = link["iconUrl"]
        except KeyError as e:
            icon_url = None
            # use library to find iconUrl if none given
            icons = favicon.get(link["href"])
            for icon in icons:
                # else have horde problem
                # gets first valid so best quality favicon
                if ".php?url=" not in icon.url:
                    icon_url = icon.url
                    break
            
            # found no valid iconUrl 
            if not icon_url: 
                print("Found no favicon for " + link["href"])
                print(icons)
                continue

        # could also use new webp or other next gen formats
        # but webP not supported in safari
        # thanks to https://stackoverflow.com/a/27253809
        icon_name_new_extension = b64encode(icon_url.encode()).decode() + '.png'
        webLink = '/static/' + icon_name_new_extension

        # create dist folder if new and construct path
        static_path = 'dist/static/'
        if not os.path.exists(static_path):
            os.makedirs(static_path)
        path = static_path + icon_name_new_extension

        # get and cache iconImages or relink if existing
        if icon_url in iconsDownloadedUrls:
            data["links"][index]["iconUrl"] = webLink
        else:
            response = requests.get(icon_url)
            if response and response.ok:
                print("Cached " + icon_url + "...")
                img = Image.open(BytesIO(response.content))

                # resize to 150px width and height
                basewidth = 150
                # would be to calculate height via aspect ratio
                # wpercent = (basewidth/float(img.size[0]))
                # hsize = int((float(img.size[1])*float(wpercent)))
                # img = img.resize((basewidth,hsize), Image.ANTIALIAS)
                img = img.resize((basewidth,basewidth), Image.ANTIALIAS)

                # convert to rgba for png file, save and relink
                img.convert('RGBA')
                img.save(path)
                data["links"][index]["iconUrl"] = webLink
                iconsDownloadedUrls.append(icon_url)
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

            print("-------- Rendering " + subject + "----------")
            site = Site.make_site(
                searchpath="./templates/subjects",
                outpath="dist/" + subject,
                env_globals=data)
            site.render()
            createManifest(subject,data["title"],data["color"], data["backgroundColor"], '..')
            createLinksJson(data["links"], subject)
    
            # have to move this service worker file because of scope reasons into base folder not keep in static 
            move(f"dist/{subject}/static/subject-files-cache-worker.js", f"dist/{subject}/subject-files-cache-worker.js")
    return subjectLinks

def renderHomepage(subjectLinks):
    # homepage site to copy static files
    # and link to all subjects
    print("===> Rendering homepage...")
    site = Site.make_site(
        searchpath="./templates/main",
        outpath="dist/",
        staticpaths=["static/"],
        env_globals={
            "title": "Hauptseite",
            "links": subjectLinks
        })
    site.render()
    # don't actually need a manifest for the index page
    # only useful for specifc course with offline caching and so on
    # would be uneeded clicks anyways 
    # createManifest()

def createCoursesJson(subjectLinks):
    courseJsonPath = 'dist/courses.json'
    # write json file for dropdown of courses links in wuex extension
    with open(courseJsonPath, 'w', encoding='utf-8') as outfile:
        print("Creating courses.json...")
        json.dump(subjectLinks, outfile)

def createLinksJson(servicesLinks, courseName):
    linkJsonPath = f"dist/{courseName}/links.json"
    # write json file with all links available to course
    # can be used by apis and bots as api without parsing
    with open(linkJsonPath, 'w', encoding='utf-8') as outfile:
        print(f"Creating links.json for {courseName}...")
        json.dump(servicesLinks, outfile)

if __name__ == "__main__":
    try:
        # clear dist folder and does not ignore errors
        rmtree('./dist/', False)
    except Exception as e:
        print(e)

    subjectLinks = renderSubjectPages()
    renderHomepage(subjectLinks)
    createCoursesJson(subjectLinks)
