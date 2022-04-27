import disnake
from disnake.ext import commands
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import asyncio

class Grade_Sorter:
    def __init__(self):
        self.class__ = 0
        self.counter = 0
        self.classss = 0

    def get_data(self, soup):
        table = soup.find("table", class_="list")
        children = table.findChildren("tr")
        data = {}
        for child in children:
            childreen = child.findChildren("td")
            for childd in childreen:
                if self.counter == 0:
                    text = str(childd.text)
                    text = text.replace("\n", "")
                    data[f"{text}"] = []
                    self.counter = 1
                    self.class__ = text
                else:
                    text = str(childd.text)
                    text = text.replace("\n", "")
                    data[f"{self.class__}"].append(text)
            self.counter = 0
        return data

    def gen_data(self, data):
        new_data = {}
        # print(data)
        for idx, val in enumerate(data):

            if idx % 2 == 0:
                text = val
                text = text.replace(" ", "")
                new_data[f"{self.classss}"] = text
            elif idx%2 == 1:
                text= val
                lower_bound = self.get_low(text)
                upper_bound = self.get_high(text)
                text = text[lower_bound:]
                text = text[:upper_bound]
                # print(text+ "----")
                self.classss = text
                new_data[f"{self.classss}"] = 0
        return new_data

    def get_low(self, val):
        for idx, vall in enumerate(val):
            if vall != " ":
                return idx

    def get_high(self, val):
        # print(val)
        for idx, vall in enumerate(val):
            if idx != 0 and val[-idx] != " ":
                # print(val[-idx])
                return -idx + 1

    def copy_get_high(self, val):
        # print(val)
        for idx, vall in enumerate(val):
            if idx != 0 and val[-idx] != " ":
                # print(val[-idx])
                return -idx + 1
            elif idx == 0 and val[-idx] != " ":
                return val

class General_info():
    def __init__(self):
        self.class__ = 0
        self.counter = 0
        self.classss = 0

    def get_data(self, soup: BeautifulSoup):
        children = soup.find_all("table", class_="list")
        # print(children)
        more_children = children[0].find_all("tr", class_="listroweven")
        img_src = more_children[0].find("img")['src']
        data = []
        for child in more_children:
            text = child.text
            text = text.replace("\n", "")
            text = text.replace(" ", "")
            data.append(text)
        data[0] = img_src
        return data

    def get_courses(self, soup: BeautifulSoup):
        courses = {}
        table = soup.find("table", class_="list")
        children = table.find_all("tr")[1:]
        counter = 0
        for child in children:
            tds = child.find_all("td")
            for idx, td in enumerate(tds):

                thingy = Grade_Sorter()
                text = td.text
                low = thingy.get_low(text)
                high = thingy.copy_get_high(text)
                if isinstance(high, str):
                    text = text
                else:
                    text = text[low:]
                    text = text[:high]

                text = text.replace("\n", "")

                if idx == 0:
                    courses[f"{counter + 1}"] = [text]
                else:
                    if not text == "":
                        courses[f"{counter + 1}"].append(text)
            counter += 1
        return courses


class get_the_grade_from_website:
    def __init__(self):
        return

    @staticmethod
    async def get(email, password):
        option = webdriver.ChromeOptions()
        option.add_argument('headless')
        option.add_argument('--user-agent=Chrome/77')
        driver = webdriver.Chrome(
            r'C:\Users\Eddie\PycharmProjects\Input_Thingy\venv\Lib\site-packages\seleniumbase\drivers/chromedriver.exe',options=option)
        driver.implicitly_wait(30)
        # print("going to website")
        driver.get("https://parents.mtsd.k12.nj.us/genesis/sis")
        # print("finding username")
        username = driver.find_element(By.ID, "j_username").send_keys(f"{email}")
        # print("finding username done")
        # print("finding password")
        password = driver.find_element(By.ID, "j_password").send_keys(f"{password}")
        #  print('done')

        # print("logining in")
        # print(driver.page_source)
        test_button4 = driver.find_elements(By.CSS_SELECTOR, 'input.saveButton')
        submit_element = [x for x in test_button4 if x.get_attribute('type') == 'submit']
        submit_element[0].click()

        # print('done')

        # print("getting data for student id and birthday and grade and name and consuler")

        general_info = General_info()
        soup1 = BeautifulSoup(driver.page_source, "html.parser")
        # print(driver.page_source)
        info = general_info.get_data(soup1)

        # print("done")
        # print("checking gradebook")

        # driver.refresh()
        # driver.refresh()
        # driver.refresh()
        # print(driver.page_source)
        thing = driver.find_elements(By.CSS_SELECTOR, 'span.headerCategoryTab')
        submit_element = [x for x in thing if x.text == "Grading"]
        submit_element[0].click()
        # print('done')
        # print("fetching grades....\n\n")

        soup = BeautifulSoup(driver.page_source, "html.parser")
        courses = general_info.get_courses(soup)

        thing = driver.find_elements(By.CSS_SELECTOR, 'span.headerCategoryTab')
        submit_element = [x for x in thing if x.text == "Gradebook"]
        submit_element[0].click()

        soup = BeautifulSoup(driver.page_source, "html.parser")
        thing = Grade_Sorter()
        data = thing.get_data(soup)

        # print("data")
        grades = thing.gen_data(data)
        # print(data)
        return (info, grades, courses)


class GetGrade(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.slash_command(name="mygrade_testing", description="Check your grades and other stats with ease", guild_ids=[958488149724635146])
    async def get_grade(
            self,
            inter: disnake.ApplicationCommandInteraction,
            email: str,
            password: str,
    ):
        channel = inter.channel
        async with channel.typing():
            await inter.response.send_message(f"Getting your grades (may take a while)... Note that {self.bot.tos}", ephemeral=True)
            grade = get_the_grade_from_website()
            try:
                grades = await grade.get(f"{email}", password)
            except IndexError:
                await inter.response.send_message(f"Check whether you typed your email or password correctly!")
                return
            new_data = {}
            info = grades[0]
            for item in grades[1].items():
                if item[0] != '0':
                    new_data[item[0]] = item[1]
            description = ""
            for item in new_data.items():
                description += f"`{item[0]}`: {item[1]}\n"

            thing = "```"
            for item in info:
                if not str(item).startswith("/genesis/sis/photos?"):
                    thing += f"{item}\n"
            thing += "```"
            description += thing

            # print(grades[0])
            # print(grades[1])
            # print(grades[2])

            sum_of_grades_point = 0
            sum_of_credits = 0
            sum_weighted_course_grade = 0
            for item in grades[2].items():
                info = item[1]
                for itemm in grades[1].items():
                    courses_grade = itemm[1]
                    courseeee = itemm[0]
                    # print(courses_grade)
                    if courses_grade != "Courses" and 'NotGradedMP' not in str(courses_grade):
                        if str(info[0]).replace(" ", "") == str(courseeee).replace(" ", ""):
                            creditss = str(info[4]).replace(" ", "")
                            creditss = float(creditss)
                            course_grade = str(courses_grade)
                            course_grade = course_grade.replace("%", "")
                            course_grade = float(course_grade)
                            w_course_grade = course_grade
                            if "Honor" or "honor" in str(courseeee):
                                w_course_grade += 5.0
                            sum_weighted_course_grade += w_course_grade*creditss
                            sum_of_credits += creditss
                            sum_of_grades_point += creditss*course_grade
            unweighted_gpa = sum_of_grades_point/sum_of_credits
            unweighted_gpa = round(unweighted_gpa, 2)
            weighted_gpa = sum_weighted_course_grade/sum_of_credits
            weighted_gpa = round(weighted_gpa,2)

            # need way to find credit of each course

            # print(info)

            embed = disnake.Embed(title=f"{inter.author.name}'s School Status", description=description, color=disnake.Color.random())
            embed.set_author(name=f"Unweighted GPA: {unweighted_gpa} || Weighted GPA: {weighted_gpa}")
            embed.set_footer(text=f"Note that {self.bot.tos}", icon_url=inter.author.avatar.url)
            embed.set_thumbnail(self.bot.user.avatar.url)
            await inter.author.send(embed=embed)
            await channel.send(f"{inter.author.mention} check your dms!")

            return