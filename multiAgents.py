# multiAgents.py
# --------------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
#
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from util import manhattanDistance
from game import Directions
import random
import util
from game import Agent

from functools import partial
from math import inf, log
import numpy as np

from searchAgents import mazeDistance, FoodSearchProblem, foodHeuristic


def ln(x): return log(x) if x > 0 else -inf


class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """

    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action)
                  for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(
            len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices)  # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()

        distToPacman = partial(manhattanDistance, newPos)

        def ghostF(ghost):
            dist = distToPacman(ghost.getPosition())
            if ghost.scaredTimer > dist:
                return inf
            if dist <= 1:
                return -inf
            return 0
        ghostScore = min(map(ghostF, newGhostStates))

        distToClosestFood = min(
            map(distToPacman, newFood.asList()), default=inf)
        closestFoodFeature = 1.0 / (1.0 + distToClosestFood)

        return successorGameState.getScore() + ghostScore + closestFoodFeature


def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()


class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers. Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn='scoreEvaluationFunction', depth='2'):
        self.index = 0  # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)


class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """

        def minimax(state, depth, agent):
            '''
                Returns the best value-action pair for the agent
            '''
            nextDepth = depth-1 if agent == 0 else depth
            if nextDepth == 0 or state.isWin() or state.isLose():
                return self.evaluationFunction(state), None

            bestOf, bestVal = (max, -inf) if agent == 0 else (min, inf)
            nextAgent = (agent + 1) % state.getNumAgents()
            bestAction = None
            for action in state.getLegalActions(agent):
                successorState = state.generateSuccessor(agent, action)
                valOfAction, _ = minimax(successorState, nextDepth, nextAgent)
                if bestOf(bestVal, valOfAction) == valOfAction:
                    bestVal = valOfAction
                    bestAction = action
            return bestVal, bestAction

        val, action = minimax(gameState, self.depth+1, self.index)
        return action


class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the alpha-beta pruned minimax action using self.depth and self.evaluationFunction
        """

        def alphaBeta(state, depth, alpha, beta, agent):
            isMax = agent == 0
            nextDepth = depth-1 if isMax else depth
            if nextDepth == 0 or state.isWin() or state.isLose():
                return self.evaluationFunction(state), None

            nextAgent = (agent + 1) % state.getNumAgents()
            bestVal = -inf if isMax else inf
            bestAction = None
            bestOf = max if isMax else min

            for action in state.getLegalActions(agent):
                successorState = state.generateSuccessor(agent, action)
                valOfAction, _ = alphaBeta(
                    successorState, nextDepth, alpha, beta, nextAgent)
                if bestOf(bestVal, valOfAction) == valOfAction:
                    bestVal, bestAction = valOfAction, action

                if isMax:
                    if bestVal > beta:
                        return bestVal, bestAction
                    alpha = max(alpha, bestVal)
                else:
                    if bestVal < alpha:
                        return bestVal, bestAction
                    beta = min(beta, bestVal)

            return bestVal, bestAction

        _, action = alphaBeta(gameState, self.depth+1, -inf, inf, self.index)
        return action


class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        agent = self.index
        if agent != 0:
            return random.choice(state.getLegalActions(agent))

        def expectimax(state, depth, agent):
            '''
                Returns the best value-action pair for the agent
            '''
            nextDepth = depth-1 if agent == 0 else depth
            if nextDepth == 0 or state.isWin() or state.isLose():
                return self.evaluationFunction(state), None

            nextAgent = (agent + 1) % state.getNumAgents()
            legalMoves = state.getLegalActions(agent)
            if agent != 0:
                prob = 1.0 / float(len(legalMoves))
                value = 0.0
                for action in legalMoves:
                    successorState = state.generateSuccessor(agent, action)
                    expVal, _ = expectimax(successorState, nextDepth, nextAgent)
                    value += prob * expVal
                return value, None

            bestVal, bestAction = -inf, None
            for action in legalMoves:
                successorState = state.generateSuccessor(agent, action)
                expVal, _ = expectimax(successorState, nextDepth, nextAgent)
                if max(bestVal, expVal) == expVal:
                    bestVal, bestAction = expVal, action
            return bestVal, bestAction

        _, action = expectimax(gameState, self.depth+1, self.index)
        return action


foodSearch = None


def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """

    pos = currentGameState.getPacmanPosition()
    food = currentGameState.getFood()
    ghostStates = currentGameState.getGhostStates()

    distToPacman = partial(mazeDistance, currentGameState, pos)

    def ghostF(ghost):
        ghostPos = tuple(map(int, ghost.getPosition()))
        ghostToPacmanDistance = distToPacman(ghostPos)
        if ghostToPacmanDistance <= 1:
            if ghost.scaredTimer >= 1:
                return inf
            return -inf
        return 0
    ghostScore = min(map(ghostF, ghostStates))

    # distToClosestFood = min(map(distToPacman, food.asList()), default=inf)
    # closestFoodFeature = 1.0 / (0.1 + distToClosestFood)

    global foodSearch
    if foodSearch == None:
        foodSearch = FoodSearchProblem(currentGameState)
    numFood = len(food.asList())
    foodEaten = len(foodSearch.start[1].asList()) - numFood
    # totalFoodFeature = 1.0 / (0.1 + numFood)
    if numFood < 20:
        closestFoodFeature = 1.0 / \
            (1.0 + foodHeuristic((pos, food), foodSearch))
    else:
        closestFoodFeature = 0
    return ghostScore + closestFoodFeature + foodEaten


# Abbreviation
better = betterEvaluationFunction
