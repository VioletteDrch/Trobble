import Phaser from "phaser";
import { CardMechanics } from "../public/src/cards/card-mechanics";
import {
  retrieveImages,
  retrieveSoundEffects,
} from "../public/src/resources/resource-puller";
import { gameRules, gameState, sizes } from "../config/gameConfig";

export default class GameScene extends Phaser.Scene {
  constructor() {
    super("scene-game");
  }

  cardMechanics = new CardMechanics(this);

  preload() {
    this.fetchImages();
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
      0xfff00,
      () => {}
    );
    this.createPlayerCard();
    this.createVictorySign();
    this.events.on("anotherPlayerScored", this.putOtherPlayersCardOnPile, this);
    this.events.on("gameEnd", this.gameEnd, this);
    this.simulateOtherPlayerScoring();
  }

  update() {}

  updateMiddleCard() {

  }

  updatePlayersCard() {

  }

  createPlayerCard() {
    this.cardMechanics.createCard(
      150,
      370,
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

  fetchImages(){
    fetch(`${api.host()}/game_logic/get_images`)
        .then(response => response.json())
        .then(data => {
          data.forEach((url, index) => {
            const key = `image_${index}`;
            this.load.image(key, url);
          });
        })
        .catch(error => {
          console.error("Error fetching images:", error);
        });
  }
}