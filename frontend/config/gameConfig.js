export const sizes = {
  width: 320,
  height: 500,
};

export const gameState = {
  pileSize: 1,
  activeAnimations: [],
  middleCard: {
    "id": 0,
    "combination": []
  },
  blocked: false,
  gameId: "",
};

export const playerInfo = {
  id: 0,
  name: "andre",
  color: 0x0000ff,
};

export const gameRules = {
  totalAmountOfCards: 10,
  pilePosition: { x: 150, y: 130 },
};
