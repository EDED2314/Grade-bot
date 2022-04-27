from dotenv import load_dotenv
import os
load_dotenv()

from GradeBot import GradeBot
from GradeBot import GetGrade

bot = GradeBot()


if __name__ == '__main__':
    bot.add_cog(GetGrade(bot))
    bot.run(os.getenv("TOKEN"))