# Wuel

## How to build manually
Prerequisite: Your python environment is python3
```sh
pip install -r requirements.txt
python build.py
```
Then the build is in the dist folder

## Ci Build and CD
The master branch is built via the `build.yaml` workflow for github pages.
If successful the build is then available on [wuel.de](https://wuel.de/) 

## Adding new courses
Every course is represented by a json file in the subjects folder.
A `course.json` follows this schema
```json
{
    "title": "Course name",
    "backgroundColor": "#333",
    "color": "#fff",
    "links": [
        {
            "name": "Wuestudy",
            "href": "https://wuestudy.zv.uni-wuerzburg.de",
            "iconUrl": "https://wuestudy.zv.uni-wuerzburg.de/HISinOne/images/logos/touch_icon_apple_retina_wue.png"
        },
        {
            "name": "Wuecampus2",
            "href": "https://wuecampus2.uni-wuerzburg.de/moodle/"
        }
    ]
}
```
To add new courses copy the `basic.json` edit the fields and add new links.
The `iconUrl` property is optional. The software tries to retrieve the icon itself if not given but for some urls like images it needs to be linked explicitly.
This new course is then served under the name of the json as path.
On the next build it should be linked on the main page, available as seperate page and if built to wuel.de also included in the dropdown of wueXtension to choose from.

## Built files
Look in the `gh-pages` to see all files which are built by the build script `build.py`. In addition to the pages a `courses.json` file get's created for wueXtension to populate it's course choosing dropdown with
