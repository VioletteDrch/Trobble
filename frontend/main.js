import "./style.css";
import Phaser from "phaser";
import { CardMechanics } from "./public/src/cards/card-mechanics";
import {
  retrieveImages,
  retrieveSoundEffects,
} from "./public/src/resources/resource-puller";

const sizes = {
  width: 300,
  height: 500,
};

const gameState = {
  points: 0,
  pileSize: 1,
  playerName: "andre",
  currentAnimations: [],
};

const gameRules = {
  totalAmountOfCards: 10,
  pilePosition: { x: 150, y: 130 },
};

class GameScene extends Phaser.Scene {
  constructor() {
    super("scene-game");
  }

  cardMechanics = new CardMechanics(gameState, gameRules, this);

  preload() {
    retrieveImages().forEach((image) => {
      this.load.image(image.name, image.url);
    });
    retrieveSoundEffects().forEach((sound) => {
      this.load.audio(sound.name, sound.url);
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
    this.cardMechanics.createCard(
      150,
      380,
      gameState.playerName,
      0x0000ff,
      () => {
        this.createPlayerCard();
      }
    );
  }

  putOtherPlayersCardOnPile() {
    const otherPlayersCard = this.cardMechanics.createCard(
      300,
      300,
      "violette",
      0x7f00ff,
      () => {}
    );
    gameState.currentAnimations = this.cardMechanics.score(otherPlayersCard);
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
    this.shade.setAlpha(1);
    this.tweens.add({
      targets: this.victorySign,
      scale: { from: 0, to: 1 },
      alpha: { from: 0, to: 1 },
      duration: 1000,
      ease: "Bounce.easeOut",
    });
  }

  createVictorySign() {
    this.shade = this.add.graphics();
    this.shade.fillStyle(0x000000, 0.7);
    this.shade.fillRect(0, 0, sizes.width, sizes.height);
    this.shade.setAlpha(0);
    this.shade.setDepth(60);

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
    this.victorySign.setDepth(70);
  }

  isGameActive() {
    return gameState.pileSize <= gameRules.totalAmountOfCards;
  }
}

const config = {
  type: Phaser.WEBGL,
  width: sizes.width,
  height: sizes.height,
  canvas: gameCanvas,
  physics: {
    default: "arcade",
    arcade: {
      gravity: { y: 0 },
      debug: false,
    },
  },
  scene: [GameScene],
};

const game = new Phaser.Game(config);
