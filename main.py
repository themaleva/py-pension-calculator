import sys
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QLineEdit, QCheckBox, QVBoxLayout, QPushButton, QTableWidget, QTableWidgetItem, QHBoxLayout, QMessageBox, QDialog
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore


class PensionCalculatorApp(QWidget):

    # Static variables
    MAX_CONTRIBUTIONS = 60000
    INCOME_THRESHOLD_40_PCT = 50270
    TAX_TRAP_THRESHOLD = 100000

    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        layout = QVBoxLayout()

        # First horizontal group
        hlayout1 = QHBoxLayout()
        
        age_label = QLabel('Current Age:')
        self.age_input = QLineEdit(self)
        hlayout1.addWidget(age_label)
        hlayout1.addWidget(self.age_input)

        current_salary_label = QLabel('Current Salary (£):')
        self.current_salary_input = QLineEdit(self)
        hlayout1.addWidget(current_salary_label)
        hlayout1.addWidget(self.current_salary_input)

        current_pension_pot_label = QLabel('Current Pension Pot (£):')
        self.current_pension_pot_input = QLineEdit(self)
        hlayout1.addWidget(current_pension_pot_label)
        hlayout1.addWidget(self.current_pension_pot_input)

        layout.addLayout(hlayout1)

        # Second horizontal group
        hlayout2 = QHBoxLayout()
        
        expected_retirement_age_label = QLabel('Retirement Age:')
        self.expected_retirement_age_input = QLineEdit(self)
        hlayout2.addWidget(expected_retirement_age_label)
        hlayout2.addWidget(self.expected_retirement_age_input)

        predicted_salary_growth_label = QLabel('Salary Growth (%):')
        self.predicted_salary_growth_input = QLineEdit(self)
        hlayout2.addWidget(predicted_salary_growth_label)
        hlayout2.addWidget(self.predicted_salary_growth_input)

        employee_contribution_label = QLabel('Employee Contribution (%):')
        self.employee_contribution_input = QLineEdit(self)
        hlayout2.addWidget(employee_contribution_label)
        hlayout2.addWidget(self.employee_contribution_input)

        layout.addLayout(hlayout2)

        # Third horizontal group
        hlayout3 = QHBoxLayout()

        employer_contribution_label = QLabel('Employer Contribution (%):')
        self.employer_contribution_input = QLineEdit(self)
        hlayout3.addWidget(employer_contribution_label)
        hlayout3.addWidget(self.employer_contribution_input)
        
        self.avoid_40_tax_cb = QCheckBox('Avoid 40% Tax?')
        hlayout3.addWidget(self.avoid_40_tax_cb)
        
        self.avoid_100k_tax_trap_cb = QCheckBox('Avoid £100k tax trap')
        hlayout3.addWidget(self.avoid_100k_tax_trap_cb)
        
        layout.addLayout(hlayout3)

        # Calculate button
        self.calculate_button = QPushButton('Calculate!', self)
        self.calculate_button.clicked.connect(self.on_calculate_clicked)
        layout.addWidget(self.calculate_button)

        # Results table
        self.results_table = QTableWidget()
        self.results_table.setColumnCount(9)
        self.results_table.setHorizontalHeaderLabels(["Age", "Current Salary", "Employee Contributions", "Employer Contributions", "Total Contributions", "Pot Balance", "2pct Growth", "4pct Growth", "6pct Growth"])
        self.results_table.resizeColumnsToContents()
        self.results_table.verticalHeader().hide()
        layout.addWidget(self.results_table)

        # Show Chart button
        self.show_chart_button = QPushButton("Show Chart", self)
        self.show_chart_button.clicked.connect(self.show_chart)
        layout.addWidget(self.show_chart_button)

        self.setLayout(layout)
        self.resize(1000, 600)
        self.setWindowTitle('UK Pension Calculator')

    def on_calculate_clicked(self):

         # Check if both checkboxes are selected
        if self.avoid_40_tax_cb.isChecked() and self.avoid_100k_tax_trap_cb.isChecked():
            error_msg_box = QMessageBox(self)
            error_msg_box.setIcon(QMessageBox.Warning)
            error_msg_box.setWindowTitle("Input Error")
            error_msg_box.setText("Please select only one option between 'Avoid 40% Tax' and 'Avoid £100k tax trap'.")
            error_msg_box.exec_()
            return
        
        self.pot_balances = []
        self.two_percent_growth = []
        self.four_percent_growth = []
        self.six_percent_growth = []

        try:
            current_age = int(self.age_input.text())
            retirement_age = int(self.expected_retirement_age_input.text())
            current_salary = float(self.current_salary_input.text())
            salary_growth = float(self.predicted_salary_growth_input.text()) / 100
            employee_contrib = float(self.employee_contribution_input.text()) / 100
            employer_contrib = float(self.employer_contribution_input.text()) / 100
            current_pension_pot = float(self.current_pension_pot_input.text())

            self.results_table.setRowCount(retirement_age - current_age + 1)
            
            row = 0
            for age in range(current_age, retirement_age + 1):
                if age != current_age:
                    current_salary *= (1 + salary_growth)

                employee_contribution_val = current_salary * employee_contrib
                employer_contribution_val = current_salary * employer_contrib
                
                # Adjusting employee contribution if the "Avoid 40% Tax" is checked
                if self.avoid_40_tax_cb.isChecked():
                    if (current_salary - employee_contribution_val) > self.INCOME_THRESHOLD_40_PCT:
                        employee_contribution_val = current_salary - self.INCOME_THRESHOLD_40_PCT

                # Adjusting employee contribution if the "Avoid £100k tax trap" is checked
                if self.avoid_100k_tax_trap_cb.isChecked():
                    if (current_salary - employee_contribution_val) > self.TAX_TRAP_THRESHOLD:
                        employee_contribution_val = current_salary - self.TAX_TRAP_THRESHOLD

                total_contributions = employee_contribution_val + employer_contribution_val

                # Check if total contributions exceed MAX_CONTRIBUTIONS
                if total_contributions > self.MAX_CONTRIBUTIONS:
                    excess_amount = total_contributions - self.MAX_CONTRIBUTIONS
                    employee_contribution_val -= excess_amount
                    total_contributions = self.MAX_CONTRIBUTIONS

                # Calculate growth balances
                if age == current_age:  # First year, there's no previous balance
                    two_percent_balance = current_pension_pot * 1.02 + total_contributions
                    self.two_percent_growth.append(total_contributions)
                    four_percent_balance = current_pension_pot * 1.04 + total_contributions
                    self.four_percent_growth.append(total_contributions)
                    six_percent_balance = current_pension_pot * 1.06 + total_contributions
                    self.six_percent_growth.append(total_contributions)
                else:
                    two_percent_balance = self.two_percent_growth[-1] * 1.02 + total_contributions
                    self.two_percent_growth.append(two_percent_balance)
                    
                    four_percent_balance = self.four_percent_growth[-1] * 1.04 + total_contributions
                    self.four_percent_growth.append(four_percent_balance)

                    six_percent_balance = self.six_percent_growth[-1] * 1.06 + total_contributions
                    self.six_percent_growth.append(six_percent_balance)

                current_pension_pot += total_contributions
                self.pot_balances.append(current_pension_pot)

                self.results_table.setItem(row, 0, QTableWidgetItem(f"{age}"))
                self.results_table.setItem(row, 1, QTableWidgetItem(f"£{current_salary:,.2f}"))
                self.results_table.setItem(row, 2, QTableWidgetItem(f"£{employee_contribution_val:,.2f}"))
                self.results_table.setItem(row, 3, QTableWidgetItem(f"£{employer_contribution_val:,.2f}"))
                self.results_table.setItem(row, 4, QTableWidgetItem(f"£{total_contributions:,.2f}"))
                self.results_table.setItem(row, 5, QTableWidgetItem(f"£{current_pension_pot:,.2f}"))
                self.results_table.setItem(row, 6, QTableWidgetItem(f"£{two_percent_balance:,.2f}"))
                self.results_table.setItem(row, 7, QTableWidgetItem(f"£{four_percent_balance:,.2f}"))
                self.results_table.setItem(row, 8, QTableWidgetItem(f"£{six_percent_balance:,.2f}"))

                row += 1

            self.results_table.resizeColumnsToContents()

        except ValueError:
            print("Please enter valid values for all fields!")

    def show_chart(self):
        # Create a QDialog for the chart
        chart_dialog = QDialog(self)
        chart_dialog.setWindowTitle("Pot Balance Chart")
        chart_dialog.resize(800, 600)
        
        # Create the plot widget inside this dialog
        plot_widget = pg.PlotWidget(chart_dialog)
        plot_widget.setGeometry(30, 30, 740, 540)  # Adjust as necessary
        
        ages = list(range(int(self.age_input.text()), int(self.expected_retirement_age_input.text()) + 1))

        plot_widget.plot(ages, self.pot_balances, clear=True)

        # Show the QDialog with the chart
        chart_dialog.exec_()


# Running the app
app = QApplication(sys.argv)
window = PensionCalculatorApp()
window.show()
sys.exit(app.exec_())
