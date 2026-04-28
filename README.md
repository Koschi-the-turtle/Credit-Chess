# CREDIT CHESS
Chess is very complex game which requires a lot of reflexion, beating your opponent requires imagining possible scenarios as far as possible in time, in order to counter your opponent's moves.

However, I'm genuinely crap at chess, therefore, to avoid getting beaten by 8 year olds on chess.com, I decided to make my own chess game, with my own rules.

Credit chess implements a new array of complex mechanics : Finance

My game combines chess with real life problems like taxes, loans, rent and more.
You could say it's a kind of educational game for kids (just now thinking I forgot to implement gambling too)

# Here's how it works : 

# Income, balance and debt
At the top and bottom of the chess board you'll find your Balance, Debt and Upkeep values.
Every of their turn, players gain a certain amount of money:
 Money = number of pawns * 220$
but they also lose a certain amount for upkeep/maintenance:

  Upkeep = number of Knights * 199$ + number of Rooks and Bishops * 120$ + number of Queens * 499$ + King * 295$
  
So your income is tightly linked to your ratio of pawns/other pieces.
You also gain money by capturing your opponent's pieces following this set of prices:

- Pawn = 308$
- Knight = 666$
- Rook & Bishop = 296$
- Queen = 2468$

You can go into debt pretty safely, as long as it stays under 10 000 $

# Sell pieces (aka human trafficking)
On the bottom left corner of the interface, you'll find a button called "Sell Piece",
it allows you to select one of your pieces and sell them for money following this set of prices: (different from capture prices)

- Pawn = 154$
- Knight = 333$
- Rook & Bishop = 148$
- Queen = 1234$

You can sell as many pieces a you want each turn.

# Buy tiles
Just over the Sell Piece button, the Buy tiles button allows you to purchase any of the current empty tiles on the board for 199$, 
and each turn, if your opponent puts or keeps a piece on that tile, he must pay you rent, equal to 112$.
However, there is no symbol, text or color marking the tile, so the enemy must remember which tile he must avoid to keep his money.
Also, if the owner of one or more tiles goes into debt, all his properties get immediately sold for rent price (112$), yes, all of them, even if only a few $ in debt.

# Bank (or your tax evasion associate)
The Bank allows you to either invest, loan or withdraw a certain amount of money which you input in the Input field.
You can invest as much as you want of your own money, and every turn you'll get a 5% return, however, you can only withdraw your money 5 turns minimum
after you invested it. You can also loan up to 10 000$, but you'll have to pay back 10% of it within 10 turns, then the next 10% within the next 10 etc.
At the end, when the loan is fully paid back, you will have to pay the bank a bonus:

  bonus = number of turns taken to pay the loan back * 10
  
which is not that bad honestly.

oh and also, the money invested in the bank isn't taxed, because, well, you made a deal with the bank so that they keep it secret...

# Taxes
Every 10 turns, both players must pay a certain amount of money:

  Tax = 20% of (player balance + amount of pieces * 3 + number of rented tiles * rent price)
  
Using the Tax button, you can see how much taxes you last paid and in how much time you'll next have to pay taxes.

The money in the bank isn't taxed, but who knows, maybe the IRS might catch you...

# How to run
Simply download the release zip file and run the .exe file
