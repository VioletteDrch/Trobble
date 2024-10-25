import {
  getImagePositions,
  getImageAngles,
} from "../resources/resource-puller";
import {
  gameRules,
  gameState,
  playerInfo,
  sizes,
} from "../../../config/gameConfig";
import {buildBaseWSMessage} from "../../../config/serverConfig.js";

export class CardMechanics {
  constructor(scene) {
    this.scene = scene;
    this.ws = scene.ws;
    this.totalImagesPerCard = 8;
  }

  getRandomPosition(list) {
    return Math.floor(Math.random() * list.length);
  }

  isGameActive() {
    return gameState.pileSize <= gameRules.totalAmountOfCards;
  }

  score(card) {
    card.setDepth(gameState.pileSize++);
    return this.moveCardToPile(card, gameRules.pilePosition);
  }

  moveCardToPile(card, pilePosition) {
    const highlight = this.scene.add.graphics();
    const sound = this.scene.sound.add(card.playerName);
    sound.play();
    const glowColor = card.playerColor;
    const steps = 6;
    const nameText = this.scene.add.text(
      card.x,
      card.y - card.displayHeight / 2,
      card.playerName,
      {
        font: "16px Arial",
        fill: "#ffffff",
        align: "center",
      }
    );
    nameText.setOrigin(0.5, 0.5);

    gameState.activeAnimations.forEach((animation) => {
      if (animation) {
        animation.destroy();
      }
    });

    this.scene.tweens.add({
      targets: card,
      x: pilePosition.x,
      y: pilePosition.y,
      duration: 500,
      ease: "Power2",
      onUpdate: () => {
        highlight.clear();

        for (let i = 0; i < steps; i++) {
          const radius = card.displayWidth / 2 + i * 2 + 10;
          const alpha = 1 - i * (1 / steps);
          highlight.lineStyle(2, glowColor, alpha);
          highlight.strokeCircle(card.x, card.y, radius);
        }

        nameText.setPosition(card.x, card.y - card.displayHeight / 2 - 15);
      },
      onComplete: () => {
        this.scene.tweens.add({
          targets: [highlight, nameText],
          alpha: 0,
          duration: 2000,
          ease: "Linear",
          onComplete: () => {
            highlight.destroy();
            nameText.destroy();
            sound.destroy();
          },
        });
      },
    });

    return [highlight, nameText, sound];
  }

  buildScoreMessage(imageId, middleCard) {
    const scoreMessage = buildBaseWSMessage(playerInfo.id, gameState.gameId);
    scoreMessage.method = "score";
    scoreMessage.payload = {
      symbol_id: imageId,
      middle_card_id: middleCard.id,
    };
    return scoreMessage;
  }

  matches(image) {
    return gameState.middleCard.combination.includes(image.id);
  }

  createImage(imageId, x, y, card) {
    // get image key from id and add it to the scene
    const imageKey = `image_${imageId}`;
    const image = this.scene.add.image(x, y, imageKey);
    image.id = imageId;

    // randomize layout
    let randomSize = 65; // Math.floor(Math.random() * 21 + 25); FIXME go back after debugging
    image.setDisplaySize(randomSize, randomSize);
    const angles = getImageAngles();
    const anglePosition = this.getRandomPosition(angles);
    image.setAngle(angles[anglePosition]);

    // bind player interactions to the image
    image.setInteractive();
    image.on("pointerdown", () => {
      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        if (this.matches(image)) {
          console.log("match !");
          const scoreMessage = this.buildScoreMessage(image.id, gameState.middleCard);
          this.ws.send(JSON.stringify(scoreMessage));
        } else {
          console.log("not a match...");
          // blockInteractions(card); TODO
        }
      } else {
        console.error("WebSocket is not open.");
      }
    });

    // add to the card and return
    card.add(image);
    return image;
  }

  createCard(x, y, cardId, cardCombination, playerName, playerColor) {
    const card = this.createContainerWithCircle(x, y);
    card.playerName = playerName;
    card.playerColor = playerColor;
    card.id = cardId;
    card.combination = cardCombination;

    const imagePositions = getImagePositions();
    for (let i = 0; i < this.totalImagesPerCard; i++) {
      let imageId = card.combination[i];
      const positionIndex = this.getRandomPosition(imagePositions);
      const position = imagePositions.splice(positionIndex, 1)[0];
      this.createImage(imageId, position.x, position.y, card);
    }

    return card;
  }

  updateMiddleCardWithNewlyCreatedCard(
    imageCombination,
    playerName,
    playerColor
  ) {
    const middleCard = this.createCard(
      300,
      300,
      imageCombination,
      playerName,
      playerColor
    );
    this.score(middleCard);
    return middleCard;
  }

  updatePlayersCard(newCard) {
    console.log("creating new top card, id = " + newCard.id);
    return this.createCard(
      150,
      370,
        newCard.id,
        newCard.combination,
      playerInfo.name,
      playerInfo.color
    );
  }

  createContainerWithCircle(x, y) {
    const card = this.scene.add.container(x, y);
    const circle = this.scene.add.graphics();
    circle.fillStyle(0xfffff0, 1);
    circle.fillCircle(0, 0, 110);
    const shadow = this.scene.add.graphics();
    shadow.fillStyle(0x000000, 0.5);
    shadow.fillCircle(5, 5, 110);
    card.add(shadow);
    card.add(circle);
    card.setSize(200, 200);
    return card;
  }

  blockInteractions(card) {
    gameState.blocked = true;
    //todo: add some graphic representation on the players card
  }
}