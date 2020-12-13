from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QFormLayout, QLineEdit

class InputDialog(QDialog):
    def __init__(self, parent=None, humanPlayers = 1):
        super().__init__(parent)
        self.textLines = []
        layout = QFormLayout(self)
        for i in range(humanPlayers):
            temp = QLineEdit(self)
            self.textLines.append(temp)
            layout.addRow(f"Full Name {i}", temp)
        self.comments = QLineEdit(self)
        buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel, self)

        layout.addRow("Experiment Comments", self.comments)
        layout.addWidget(buttonBox)

        buttonBox.accepted.connect(self.accept)
        buttonBox.rejected.connect(self.reject)

    def getInputs(self):
        output = {}
        for i, line in enumerate(self.textLines):
            output[f'fullName {i+1}'] = line.text()
        output['comments'] = self.comments.text()
        return output
