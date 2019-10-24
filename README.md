# PRO. CO. : A Game on Consumerism

### UPDATE 10/24/19
Due to Scikit-Learn's GradientBoostingRegressor from version 0.20.1 to 0.21.2, the `SmartConsumer` class (see below) is broken. The `SmartConsumer` class should not be used, 
do not input `s` for the question `WHAT WOULD YOU LIKE TO BE??`

In order to use the `SmartConsumer`, please refer to relevant training code in this file, modify and run training code to make your own `SmartConsumer`. 

Apologies for the inconvenience. 

## A Brief Description
This game takes place in a world with a producer and a consumer. The producer
is in charge of reproducing, in turn increasing its net worth. The consumer
consumes the product of the producer, expending its wealth in the hopes that
it will reap future rewards. The game ends when either the producer or the
consumer goes bankrupt.

## How to Play
- Download this code.
- cd into this code's directory.
- Install : `python3 setup.py install`
- Import : `from proco_game import play_game`
- Play : `play_game()`

## What is the current status of this game?
When you execute the main code of this game, you play as either a Consumer
or spectate a SmartConsumer. If you are a Consumer, you have to input values
for the controller variables. Then you move against the Producer until either one
of you go bankrupt. If you spectate a SmartConsumer, you just sit back and
watch how a Consumer powered by good data inserted into a basic black-box machine
learning algorithm will probably perform better than you.

Some important features have not yet been coded. These include specifying a first-mover
(default is set to producer), an equivalently `SmartProducer` for the existing
`SmartConsumer`, and more intricately thought-out machine learning work to
train these players (currently is using lone scikit-learn function call).

On the topic of machine learning, there is always room for improvement
with regards to the `SmartConsumer`. The `SmartConsumer` is currently able to
best any given `Producer` with odds consistently greater than 70%. With more thought
put into the training algorithms, the `SmartConsumer` will certainly
grow smarter.

## More Details
The producer and consumer will take turns moving, the first mover is decided by
the initialization of the game.

**UPDATE: Producer moves first by default. Have not yet tested moving consumer first.**

Below describes the pipeline for the producer and consumer :

**The Producer**
- get analysis on current situation
- decide what to do based on analysis
- reorganize
   1) spread assets
   2) invest in assets
   3) remove rotting units (a.k.a. consumer's possessions)
   4) duplicate units

**The Consumer**
- calculates the total amount to spend this round
   1) the maximum amount for investing in current possessions  
   2) the minimum amount for buying new units
- invest and buy
- (producer) reanalyzes the consumer's buying power and logs the variable
- deduct risk

## The Reason Behind the Details

**The World**

The World is a cold and impartial spectator. Its `tax` is arbitrarily defined
but must be met, its `risks` are also arbitrarily defined and hide behind a
corner waiting on chance. Additionally, the effects of these `risks` is the
variable `risk_effects`, and is equal to the arbitrary value of 100 x `risks`.
The only factor that brings anything outwardly new is the reproductive factor
(call it `RF`). The producer and consumer make use
of this `RF`.

**The Producer**

The producer is represented as an n x 5 matrix. Each element in this matrix
is of the form (surface_area, depth, 0-layer worth, net worth, id).

Reproduction for each non-negative unit is :
`new_net_worth = (net_worth * RF) * (1 - TAX)**depth`

Reproduction for each negative unit is :
`new_net_worth = -(-(net_worth * RF) * (1 - TAX)**depth)`

Surface area decreases costs from risk (a probabilistic event), but increases
costs from tax (a definite event). Depth decreases consumer buying power, but
stunts the growth potential of the producer.

Each element (a.k.a a unit) is consisted of `depth` layers. The `0-layer worth`
measures the current layer's worth, and the net worth is the total worth of the
element. In order for a consumer to consume a unit, it must consume all of the
layers of this element, resulting in the element having a net worth at or below
0.

The producer has control over the following variables :
- COST_ROT_THRESHOLD
- COST_TAX_THRESHOLD
- COST_RISK_THRESHOLD
- COST_STUNT_THRESHOLD
- CONSUMER_POWER_THRESHOLD

These variables, as named, are threshold values. When a producer calculates
some measure that goes above its respective threshold, it will act to fix
the corresponding qualities to make this measure return below the threshold.
Note that the measures for these variables are not absolute measures. They are
normalized by the producer's current net worth.

COST_ROT_THRESHOLD limits the negative potential of the producer's non-positive
units. These non-positive units are owned by the consumer (see the consumer section for more details). Once the value of these non-positive units cross this
threshold, the producer will clean up these non-positive units. The cost of
cleaning up each non-positive unit is :
`cost = - (unit_net_worth * RF)`

COST_TAX_THRESHOLD limits the taxation that the producer incurs from its
possessions. The cost of this taxation positively correlates to the surface
area of the producer units. The cost of taxation for each unit is :
`cost = unit_net_worth * (TAX * (1 + unit_surface_area / scaling_factor))`
This scaling factor is set at the arbitrary value of 10 ^ 6.

COST_RISK_THRESHOLD limits the risk that the producer can potential incur.
The potential risk for each unit negatively correlates with the surface area,
and is :
`costRisk = (RISK_EFFECTS * unitInfo[3]) / log(unitInfo[0])`

COST_STUNT_THRESHOLD limits the stunting that occurs to the producer the
more `depth` it adds to its units. Stunting positively correlates with `depth`,
and for each unit is equal to :
`stunt = 1 - actual_growth / (unit_net_worth * RF)`
Please see the details on reproduction above for `actual growth`.
Stunting measure for the producer is an average of the stunting for each unit.

CONSUMER_POWER_THRESHOLD limits the buying power of the consumer. The consumer's
buying power has a maximum of 1.0 (1 for 1). But when a producer unit has a depth
above 0, this buying power gets reduced. Please see section on consumer for more
details. The buying power is calculated as :
`buying_power = |consumer_expense / delta_producer_net_worth|`

**The Consumer**

The consumer has a big purse, a variable called `wealth`. The consumer uses
its wealth to purchase producer units. It does this because it hopes to gain
rewards for spending its wealth on these producer units. When a consumer is able to entirely purchase a producer unit (the producer unit has a new negative worth),
it owns the producer unit. Owning a producer unit allows the consumer to
reap `investment` rewards proportional to the amount of `wealth` it puts into
the negative unit. So if a producer reproduces and the negative unit changes in
worth, these changes will not affect the consumer's investment rewards. Another
rule about these `investments` is that only the wealth after the consumer has
purchased the unit (below 0 worth) will go towards investment rewards. There is also a `gratification` reward. If the consumer purchased a unit this round, then the consumer will reap `gratification` reward X rounds later. This reward is
equal to the net worth of the unit, and X is set to the arbitrary value of 3.

The consumer has control over the following variables :
* GREED
* FOCUS
* SPEND
* INVEST

GREED determines the maximum proportion of consumer wealth to spend this round.

FOCUS determines the maximum proportion of total spendings this round towards
currently owned possessions.

SPEND is a scalar that measures the value to put into a unit given its worth.
For example, if a unit has 100 worth, and SPEND is 3, then consumer will put 300 worth into the unit.

INVEST is a scalar that determines the value to put into each possession.
If a unit has 200 invested into it, and INVEST is 3, then the next investment
into this unit will be 600 worth.

The consumer expends its wealth on producer units of its choosing in the hopes
it can own the unit, reap gratification rewards, and have the ability to
invest more of its wealth into the unit for investment payoffs. Each producer
unit has a depth value at its index 1. This depth value determines the consumer's
buying power: a higher depth means lower consumer buying power (a dollar is less
than a dollar). Specifics for how this consumer buying power is calculated has
not yet been finalized.

## What is the point of all this?
The available controls for the producer and consumer are limited. The controls
are causal variables, meaning they do not directly impact the decision-making
of these two players, but influence their decisions to lean towards some way.

In other ways, the producer and consumer are given access to the controller
variables. But the actual decisions themselves are up to the producer and consumer; these decisions are made "randomly" since there are no
algorithms that dictate the specific quantities. Just as important is the
random risk in this world; this risk can make or break.

The intention behind this stochastic element is to test if the producer and
consumer can reliably improve their performance in a world of non-precision.

This non-precision is due to the limited controller variables of the producer and
consumer.To elaborate, the mechanisms that the producer and consumer use to move
rely on the controller variables. But the actual details behind their moves
have strong elements of randomness to them.

This is a world with arbitrarily-defined rules that the producer and
consumer operate by. The main question is then, can these two find some
method to the madness?

Please see the classes `SmartConsumer` and `SmartProducer`(not coded yet) to see for yourself.

## What is the point of all this? (UPDATED : short version)
As previously stated, `SmartProducer` has not yet been coded. The point of this
is to train a `SmartConsumer` through basic machine learning that can reliably best a non-smart Producer.
The moral here is that it pays to be informed. The `SmartConsumer` will reliably
perform better than a typical `Consumer`.

## What is the logic behind some of this code?
An economics class I took in college a long while back inspired me to code this.
A big idea I used was the concept of declining returns, for example, the
relationship between producer unit depth and consumer buying power.

## Some Technicalities
The code is not designed for big-scale operations. This means that the producer
should have a matrix representation n x 5 in which the size of the matrix is less
than half a million. If the producer surpasses this size, the game gets called off.
There are also some interesting cases where games do not end. In these cases,
the consumer and producer both prosper for indefinite time. The limit to each
game has been set to under 1000 rounds. To see for yourself, please take a
look at the code in file `make_data.py`, and execute functions accordingly.

The game, in this current state, is very computationally expensive. Games
take a long time.

## How does training take place?
We first need data. Data will be collected by running match-ups between consumer
and producer. Arguments for consumer and producer will be carefully selected.

Then this data will be used to run training algorithms.

Important variables to consider for training :

**consumer**
- risk
- change in risk
- gratification payoff
- inv. payoff
- change in payoffs
- new investments
- change in wealth

**producer**
- risk
- change in risk  
- tax
- change in tax
- growth
- change in growth
- consumer_power
- change in consumer_power
- cost_measure
- change ''
- rot
- change ''
- stunt
- change ''
- change in net worth

## What does the testing code test?
Most of these testing methods do not measure precision of operations, since
the formulas behind said operations are designed by me. However, in order
for the game to work as I intended it, certain operations must follow a
relation. An example would be consumer buying power and reproductive growth being
inversely proportional to depth of producer units.

## Is this all to this game?
The broad strokes have been covered.
