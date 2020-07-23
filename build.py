from staticjinja import Site
import os,json
from shutil import rmtree

def renderSubjectPages():
    # renders pages for all subjects
    path_to_subject_jsons = './subjects/'

    subjectLinks = []
    for file_name in [file for file in os.listdir(path_to_subject_jsons) if file.endswith('.json')]:
        subject = file_name.replace('.json', '')

        with open(path_to_subject_jsons + file_name, encoding='utf-8') as json_file:
            data = json.load(json_file)

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

    # write json file for dropdown of courses links in wuex extension
    with open('dist/courses.json', 'w', encoding='utf-8') as outfile:
        json.dump(subjectLinks, outfile)


if __name__ == "__main__":
    # clear dir folder and ignore errors if no dir folder exists
    rmtree('./dir/', True)

    subjectLinks = renderSubjectPages()
    renderHomepage(subjectLinks)
