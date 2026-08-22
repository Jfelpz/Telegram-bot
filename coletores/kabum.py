from coletores.awin import AwinFeedCollector


class KabumCollector(AwinFeedCollector):
    """
    Coletor do KaBuM! via feed de produtos da Awin.
    """

    def __init__(self):

        super().__init__(
            feed_url_env="AWIN_FEED_URL",
            loja_nome="KABUM"
        )
