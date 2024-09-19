export default class ErrorMessage {
  constructor(scene, x, y, width) {
    this.scene = scene;

    this.errorMessage = this.scene.add.text(x, y, "", {
      fontSize: "20px",
      fill: "#ffffff",
      fontStyle: "bold",
      backgroundColor: "#ff0000",
      padding: { x: 10, y: 10 },
      align: "center",
      wordWrap: { width: width, useAdvancedWrap: true },
    }).setOrigin(0.5).setVisible(false);

    this.errorMessage.setInteractive().on('pointerdown', () => {
      this.hide();
    });
  }

  show(message) {
    this.errorMessage.setText(message).setVisible(true);

    this.scene.time.delayedCall(3000, () => {
      this.hide();
    });
  }

  hide() {
    this.errorMessage.setVisible(false);
  }
}
