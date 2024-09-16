import Phaser from "phaser";
import { CardMechanics } from "../public/src/cards/card-mechanics";
import { retrieveImages } from "../public/src/images/image-puller";
import { gameRules, gameState, sizes } from "../config/gameConfig";

export default class GameScene extends Phaser.Scene {
  constructor() {
    super("scene-game");
  }

  cardMechanics = new CardMechanics(gameState, gameRules, this);

  preload() {
    retrieveImages().forEach((image) => {
      this.load.image(image.name, image.url);
    });
    this.load.image("bg", "/assets/background.jpg");
  }

  create() {
    this.add.image(0, 0, "bg").setOrigin(0, 0).setScale(0.5);
    const pile = this.cardMechanics.createCard(
      gameRules.pilePosition.x,
      gameRules.pilePosition.y,
      "pile",
      () => {}
    );
    this.createPlayerCard();
    this.createVictorySign();
    this.events.on("anotherPlayerScored", this.putOtherPlayersCardOnPile, this);
    this.events.on("gameEnd", this.gameEnd, this);
    this.simulateOtherPlayerScoring();
  }

  update() {}

  createPlayerCard() {
    this.cardMechanics.createCard(100, 100, gameState.playerName, () => {
      this.createPlayerCard();
    });
  }

  putOtherPlayersCardOnPile() {
    const otherPlayersCard = this.cardMechanics.createCard(
      300,
      300,
      "violette",
      () => {}
    );
    this.cardMechanics.score(otherPlayersCard);
  }

  simulateOtherPlayerScoring() {
    this.time.addEvent({
      delay: 2000,
      callback: () => {
        this.events.emit("anotherPlayerScored");
      },
      loop: this.isGameActive(),
    });
  }

  gameEnd(winner) {
    this.time.removeAllEvents();
    if (winner !== gameState.playerName) {
      this.victorySign.text = "YOU LOSE";
      this.victorySign.setFill("#FF0000");
    }
    this.tweens.add({
      targets: this.victorySign,
      scale: { from: 0, to: 1 },
      alpha: { from: 0, to: 1 },
      duration: 1000,
      ease: "Bounce.easeOut",
    });
  }

  createVictorySign() {
    this.victorySign = this.add.text(
      sizes.width / 2,
      sizes.height / 2,
      "YOU WIN!",
      {
        fontSize: "64px",
        fill: "#ff0",
        fontStyle: "bold",
      }
    );
    this.victorySign.setOrigin(0.5);
    this.victorySign.setAlpha(0);
  }

  isGameActive() {
    return gameState.pileSize <= gameRules.totalAmountOfCards;
  }
}
