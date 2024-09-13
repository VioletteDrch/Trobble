import {
  retrieveImages,
  getImagePositions,
  getImageAngles,
} from "../images/image-puller";

export class CardMechanics {
  constructor(gameState, gameRules, scene) {
    this.gameState = gameState;
    this.gameRules = gameRules;
    this.scene = scene;
    this.totalImagesPerCard = 7;
  }

  getRandomPosition(list) {
    return Math.floor(Math.random() * list.length);
  }

  createImage(id, x, y, card, onScoring, images) {
    const imagePosition = this.getRandomPosition(images);
    const image = this.scene.add.image(x, y, images[imagePosition].name);
    images.splice(imagePosition, 1);
    let randomSize = Math.floor(Math.random() * 21 + 25);
    image.setDisplaySize(randomSize, randomSize);
    const angles = getImageAngles();
    const anglePosition = this.getRandomPosition(angles);
    image.setAngle(angles[anglePosition]);
    image.id = id;
    image.setInteractive();
    image.on("pointerdown", () => {
      if (this.matches(image)) {
        this.score(card);
        onScoring();
      }
    });
    card.add(image);
    return image;
  }

  matches(image) {
    if (image.id === 1) {
      return this.isGameActive();
    }
    return false;
  }

  isGameActive() {
    return this.gameState.pileSize <= this.gameRules.totalAmountOfCards;
  }

  score(card) {
    card.setDepth(this.gameState.pileSize++);
    if (card.playerName === this.gameState.playerName) {
      this.gameState.points++;
    }
    if (!this.isGameActive()) {
      this.scene.events.emit("gameEnd", card.playerName);
    }
    this.moveCardToPile(card, this.gameRules.pilePosition);
  }

  moveCardToPile(card, pilePosition) {
    this.scene.tweens.add({
      targets: card,
      x: pilePosition.x,
      y: pilePosition.y,
      duration: 500,
      ease: "Power2",
    });
  }

  createCard(x, y, playerName, onScoring) {
    const card = this.createContainerWithCircle(x, y);
    card.playerName = playerName;
    const imagePositions = getImagePositions();
    const images = retrieveImages();
    for (let i = 1; i < this.totalImagesPerCard; i++) {
      const positionIndex = this.getRandomPosition(imagePositions);
      const position = imagePositions[positionIndex];
      this.createImage(i, position.x, position.y, card, onScoring, images);
      imagePositions.splice(positionIndex, 1);
    }
    return card;
  }

  createContainerWithCircle(x, y) {
    const card = this.scene.add.container(x, y);
    const circle = this.scene.add.graphics();
    circle.fillStyle(0xfffff0, 1);
    circle.fillCircle(0, 0, 100);
    const shadow = this.scene.add.graphics();
    shadow.fillStyle(0x000000, 0.5);
    shadow.fillCircle(5, 5, 100);
    card.add(shadow);
    card.add(circle);
    card.setInteractive();
    card.setSize(200, 200);
    return card;
  }
}
