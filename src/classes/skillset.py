from loguru import logger

from src.models.checklist import Checklist
from src.models.wiki_article import WikiArticle


class SkillSet:

    def __init__(self, wiki_manager, checklist_manager):

        self.wiki_loader = wiki_manager
        self.checklist_builder = checklist_manager

    def enrich(self, checklist: Checklist):
        """
        У чеклистов указывается skill, мы связываем его с таблицей скиллсета и проставляем
        - skill_slug, который пригодится для открытия статей
        - skill_name, где написано "делать штуки" вместо "делает штуки"
        :param checklist:
        :return:
        """
        for criteria in checklist.body:

            skill: WikiArticle = self.wiki_loader.find("skill", criteria["skill"])

            if skill is None:
                logger.debug(f"Не найден навык {criteria['skill']} для чеклиста {checklist.lesson}")
            else:
                criteria["skill_slug"] = skill.slug
                criteria["skill_name"] = skill.skill_name

        return checklist
