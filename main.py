from src.analyser import Analyser
from src.config import (
    TICKERS,
    EVENTS,
    START_DATE,
    END_DATE,
    PRE_WINDOW,
    POST_WINDOW,
)

def main():
    analyser = Analyser(
        tickers=TICKERS,
        events=EVENTS,
        start_date=START_DATE,
        end_date=END_DATE,
        pre_window=PRE_WINDOW,
        post_window=POST_WINDOW,
    )
    analyser.run()

if __name__ == "__main__":
    main()