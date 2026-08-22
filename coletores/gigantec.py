from coletores.awin import AwinFeedCollector


class GigantecCollector(AwinFeedCollector):
    """
    Coletor da Gigantec via feed de produtos da Awin.
    """

    def __init__(self):

        super().__init__(
            feed_url_env="AWIN_FEED_URL_GIGANTEC",
            loja_nome="GIGANTEC"
        )
