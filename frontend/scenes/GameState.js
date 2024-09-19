export default class GameState{
    constructor() {
        this.middleCard = null;
        this.playerCards = {};
    }

    updateState(newState) {
        this.middleCard = newState.middleCard;
        this.playerCard = newState.playerCard;
    }

    getMiddleCard() {
        return this.middleCard;
    }

    getPlayerCards(playerId) {
        return this.playerCards[playerId] || [];
    }
}