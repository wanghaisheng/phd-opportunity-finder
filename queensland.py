emails="""c.haslam@uq.edu.au
t.dick@uq.edu.au
r.sanchez@uq.edu.au
alej.melendez@uq.edu.au
m.tebyetekerwa@uq.edu.au
m.moni@uq.edu.au
s.grainger@uq.edu.au
a.hill@psy.uq.edu.au
c.pattinson@uq.edu.au
m.lyu@uq.edu.au
p.chen1@uq.edu.au
j.toyras@uq.edu.au
c.sherwell@uq.edu.au
c.fumeaux@uq.edu.au
s.edmed@uq.edu.au
n.cordeirodacosta@uq.edu.au
davel@itee.uq.edu.au
m.dsouza@uq.edu.au
p.leearcher@uq.edu.au
j.king16@uq.edu.au
m.kielar@uq.edu.au
trung.ngo@uq.edu.au
g.mattison@uq.edu.au
m.masud@uq.edu.au
kwheeler@uq.edu.au
n.amiralian@uq.edu.au
matthews@uq.edu.au
ksb@uq.edu.au
s.trost@uq.edu.au
simon.smith@uq.edu.au
zhigang.chen@uq.edu.au
n.dissanayaka@uq.edu.au
f.steyn@uq.edu.au
b.vicenzino@uq.edu.au
udantha@eecs.uq.edu.au
s.brauer@uq.edu.au
s.ngo@uq.edu.au
l.wang@uq.edu.au
p.hodges@uq.edu.au
a.abbosh@uq.edu.au
m.dargusch@uq.edu.au
j.zou@uq.edu.au
lovell@eecs.uq.edu.au
"""
import pandas as pd

class EmailComparator:
    def __init__(self, existing_csv, new_emails):
        self.existing_csv = existing_csv
        self.new_emails = new_emails

    def load_existing_emails(self):
        try:
            df = pd.read_csv(self.existing_csv)
            return set(df['Email'].str.strip())  # Load emails into a set for quick lookup
        except FileNotFoundError:
            print(f"File not found: {self.existing_csv}")
            return set()

    def find_new_emails(self):
        existing_emails = self.load_existing_emails()
        new_emails_set = set(self.new_emails)

        # Find emails that are in new_emails but not in existing_emails
        unique_new_emails = new_emails_set - existing_emails
        return list(unique_new_emails)

    def save_new_emails_to_csv(self, new_emails):
        if new_emails:
            df = pd.DataFrame(new_emails, columns=["Email"])
            df.to_csv("new_emails.csv", index=False)
            print("New emails saved to new_emails.csv")
        else:
            print("No new emails to save.")

if __name__ == "__main__":
    existing_csv = "queensland.csv"  # Path to the existing CSV file
    new_emails = emails
    

    comparator = EmailComparator(existing_csv, new_emails)
    unique_new_emails = comparator.find_new_emails()
    comparator.save_new_emails_to_csv(unique_new_emails)

