import React from "react"

const Game = () => {

  const [gameOver, setGameOver] = useState(true)
  const [winner, setWinner] = useState("")

  const [player1Hand, setPlayer1Hand] = useState([])
  const [player1Money, setPlayer1Money] = useState("")
  const [player2Hand, setPlayer2Hand] = useState([])
  const [player2Money, setPlayer2Money] = useState("")
  const [player3Hand, setPlayer3Hand] = useState([])
  const [player3Money, setPlayer3Money] = useState("")
  const [player4Hand, setPlayer4Hand] = useState([])
  const [player4Money, setPlayer4Money] = useState("")

  const [turn, setTurn] = useState("")
  const [playedCardsPile, setPlayedCardsPile] = useState([])
  const [drawCardsPile, setDrawCardsPile] = useState([])

  const CARDS = [
    "2d", "2c", "2h", "2s",
    "3d", "3c", "3h", "3s",
    "4d", "4c", "4h", "4s",
    "5d", "5c", "5h", "5s",
    "6d", "6c", "6h", "6s",
    "7d", "7c", "7h", "7s",
    "8d", "8c", "8h", "8s",
    "9d", "9c", "9h", "9s",
    "10d", "10c", "10h", "10s",
    "11d", "11c", "11h", "11s",
    "12d", "12c", "12h", "12s",
    "13d", "13c", "13h", "13s",
    "1d", "1c", "1h", "1s",
  ] //note: suits are useless

  useEffect(() => {
    //shuffle cards
    //set turn?

    //starting deal (2 cards)
    //show cards?? pre-flop

    //first betting??
    //--> call, check, raise, fold

    //community cards, faceup

    //second betting round??
    //--> call, check, raise, fold

    //another card
    //third betting round
    //showdown

    //burn card

    //evaluate value of deck (showdown)
    //should have hand of five
    //two hole cards, 5 community cards

    //win
    //set GameOver false
  }, [])


  return (
    <div>

    </div>
  )
}

export default Game
