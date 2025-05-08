# Name: Ming-Hsuan, Chen
# Student Number: S4055813
# The highest level I have attempted: The program has completed all HD level requirements and ensures that all low level (PASS, CREDIT, DI) requirements are met. The report.txt includes all information from the files passed in as a command line argument and the time of the report's generation.

import sys
from datetime import datetime

class EmptyFile(Exception):
    pass

class InvalidResults(Exception):
    pass


class InvalidIDFormat(Exception):
    pass

class Book:
    def __init__(self, bookID, name, book_type, ncopy, maxday, lcharge):
        self.bookID = bookID
        self.name = name
        self.book_type = book_type
        self.ncopy = ncopy
        self.maxday = maxday
        self.lcharge = lcharge
        self.borrowed_days = {}

    def update_borrowed_days(self, memberID, days):
        if days == "R":
            self.borrowed_days[memberID] = "--"
        else:
            self.borrowed_days[memberID] = int(days)

    def get_borrowed_days(self, memberID):
        if memberID in self.borrowed_days:
            return self.borrowed_days[memberID]
        else:
            return "xx"

    def display_info(self, members):
        display = []
        for m in members:
            display.append(f"{self.get_borrowed_days(m)}")
        return f"{self.bookID}" + " ".join(display)

    def calculate(self):
        nborrow = 0
        for days in self.borrowed_days.values():
            if days != "--":
                nborrow += 1

        nreserve = 0
        for days in self.borrowed_days.values():
            if days == "--":
                nreserve += 1

        borrow_days = []
        for days in self.borrowed_days.values():
            if isinstance(days, int):
                borrow_days.append(days)

        if len(borrow_days) > 0:
            min_days = min(borrow_days)
            Max_days = max(borrow_days)
            range_days = f"{min_days}-{Max_days}"
        else:
            range_days = "0-0"
        return nborrow, nreserve, range_days

class Textbook(Book):
    maxday = 14
    def __init__(self, bookID, name, ncopy, lcharge):
        super().__init__(bookID, name, "Textbook", ncopy, Textbook.maxday, lcharge)

class Fiction(Book):
    def __init__(self, bookID, name, ncopy, maxday, lcharge):
        if maxday <= 14:
            raise ValueError(f"Error: Fiction {bookID} has maxday {maxday} which is not greater than 14")
        super().__init__(bookID, name, "Fiction", ncopy, maxday, lcharge)

class Member:
    def __init__(self, memberID, first_name, last_name, dob, member_type):
        self.memberID = memberID
        self.first_name = first_name
        self.last_name = last_name
        self.dob = datetime.strptime(dob, "%d/%m/%Y")
        self.member_type = member_type
        self.borrowed_books = {}

    def add_borrowed_book(self, bookID, book_type, days):
        self.borrowed_books[bookID] = (book_type, days)

    def compute(self):
        textbooks = 0
        fictions = 0
        total_days = 0
        count = 0

        for book_type, day in self.borrowed_books.values():
            if book_type == "Textbook":
                textbooks += 1
            elif book_type == "Fiction":
                fictions += 1

            if day != "R":
                total_days += int(day)
                count += 1

        if count > 0:
            avg_days = total_days / count
        else:
            avg_days = 0
        return textbooks, fictions, avg_days

    def compute_fee(self, books):
        total_fee = 0.0
        for bookID, (book_type, days) in self.borrowed_books.items():
            if days != "R":
                borrowed_days = int(days)
                book = books[bookID]
                if borrowed_days > book.maxday:
                    total_fee += book.lcharge * (borrowed_days - book.maxday)
        return total_fee

class Standard(Member):
    def __init__(self, memberID, first_name, last_name, dob):
        super().__init__(memberID, first_name, last_name, dob, "Standard")

    def check_limits(self):
        # "_" represents a value to be ignored
        textbooks, fictions, _ = self.compute()
        if textbooks <= 1 and fictions <= 2:
            return True
        else:
            return False

class Premium(Member):
    def __init__(self, memberID, first_name, last_name, dob):
        super().__init__(memberID, first_name, last_name, dob, "Premium")

    def check_limits(self):
        # "_" represents a value to be ignored
        textbooks, fictions, _ = self.compute()
        if textbooks <= 2 and fictions <= 3:
            return True
        else:
            return False

class Record:
    def __init__(self):
        self.books = {}
        self.members = {}
        self.members_loaded = False  # Indicate if members file is read

    def validate_bookID(self, bookID):
        if not bookID.startswith("B") or not bookID[1:].isdigit():
            raise InvalidIDFormat(f"Invalid book ID format: <{bookID}>")

    def validate_memberID(self, memberID):
        if not memberID.startswith("M") or not memberID[1:].isdigit():
            raise InvalidIDFormat(f"Invalid member ID format: <{memberID}>")

    def validate_day(self, days):
        if days != "R" and not days.isdigit():
            raise InvalidResults(f"Invalid result in Record file: <{days}>")


    def read_records(self, file):
        try:
            file = open(file, "r")
            lines = file.readlines()
            if not lines:
                raise EmptyFile(f"File <{file.name}> is empty.")
            for line in lines:
                record_line = line.strip().split(",")
                bookID = record_line[0].strip()
                self.validate_bookID(bookID)
                if bookID not in self.books:
                    # Using default values for unknown books
                    self.books[bookID] = Book(bookID, "Name", "type", 0, 0, 0.0)
                for i in range(1, len(record_line)):
                    member_data = record_line[i].strip().split(":")
                    memberID = member_data[0].strip()
                    self.validate_memberID(memberID)
                    days = member_data[1].strip()
                    self.validate_day(days)
                    book_type = self.books[bookID].book_type
                    if memberID not in self.members:
                        # Using default values for unknown members
                        self.members[memberID] = Member(memberID, "first_name", "last_name", "17/06/2024", "type")
                    self.members[memberID].add_borrowed_book(bookID, book_type, days)
                    self.books[bookID].update_borrowed_days(memberID, days)
            file.close()
        except FileNotFoundError:
            print(f"File name <{file}> not found")
            sys.exit(1)
        except (EmptyFile, InvalidResults, InvalidIDFormat) as e:
            print(e)
            sys.exit(1)

    def read_books(self, file):
        try:
            file = open(file, "r")
            lines = file.readlines()
            if not lines:
                raise EmptyFile(f"File <{file.name}> is empty.")
            for line in lines:
                book_data = line.strip().split(",")
                bookID = book_data[0].strip()
                self.validate_bookID(bookID)
                name = book_data[1].strip()
                book_type = book_data[2].strip()
                ncopy = int(book_data[3].strip())
                maxday = int(book_data[4].strip())
                lcharge = float(book_data[5].strip())
                if book_type == "T":
                    if maxday != Textbook.maxday:
                        print(f"Error: Textbook {bookID} has maxday {maxday} instead of {Textbook.maxday}")
                        sys.exit(1)
                    self.books[bookID] = Textbook(bookID, name, ncopy, lcharge)
                elif book_type == "F":
                    try:
                        self.books[bookID] = Fiction(
                            bookID, name, ncopy, maxday, lcharge)
                    except ValueError as e:
                        print(e)
                        sys.exit(1)
            file.close()
        except FileNotFoundError:
            print(f"File name <{file}> not found")
            sys.exit(1)
        except (EmptyFile, InvalidIDFormat) as e:
            print(e)
            sys.exit(1)

    def read_members(self, file):
        try:
            file = open(file, "r")
            lines = file.readlines()
            if not lines:
                raise EmptyFile(f"File {file.name} is empty.")
            for line in lines:
                member_data = line.strip().split(",")
                memberID = member_data[0].strip()
                self.validate_memberID(memberID)
                first_name = member_data[1].strip()
                last_name = member_data[2].strip()
                dob = member_data[3].strip()
                member_type = member_data[4].strip()
                if memberID in self.members:
                    borrowed_books = self.members[memberID].borrowed_books
                    if member_type == "Standard":
                        self.members[memberID] = Standard(
                            memberID, first_name, last_name, dob)
                    elif member_type == "Premium":
                        self.members[memberID] = Premium(
                            memberID, first_name, last_name, dob)
                    else:
                        raise ValueError(f"Unknown member type: {member_type}")
                    self.members[memberID].borrowed_books = borrowed_books
            file.close()
            self.members_loaded = True  # Set the flag to True when members are loaded
        except FileNotFoundError:
            print(f"File name <{file}> not found")
            sys.exit(1)
        except (EmptyFile, InvalidIDFormat) as e:
            print(e)
            sys.exit(1)

    def display_records(self):
        if not self.books:
            print("No records to display")
            return

        member_list = list(self.members.keys())
        member_list.sort()
        book_list = list(self.books.keys())
        book_list.sort()

        # Formatted messages
        print("\nRECORDS")
        header = "| Member IDs "
        for book in book_list:
            header += f"{book:>6}"
        print("-" * (len(header) + 2))
        print(header + " |")
        print("-" * (len(header) + 2))

        for member in member_list:
            row = f"| {member:<11}"
            for book in book_list:
                row += f"{self.books[book].get_borrowed_days(member):>6}"
            print(row + " |")

        print("-" * (len(header) + 2))
        print("RECORDS SUMMARY")
        total_books = len(self.books)
        total_members = len(self.members)
        total_days = 0
        count = 0

        for book in self.books.values():
            for day in book.borrowed_days.values():
                if day != "--":
                    total_days += int(day)
                    count += 1
        if count > 0:
            average_days = round(total_days / count, 2)
        else:
            average_days = 0

        print(f"There are {total_members} members and {total_books} books.")
        print(f"The average number of borrow days is {average_days:.2f} (days).\n")

    def display_books(self):
        # Display textbook information
        print("TEXTBOOK INFORMATION")
        print("-" * 97)
        header_format = "| {0:<12} {1:<12} {2:<12} {3:<7} {4:<8} {5:<9} {6:<9} {7:<10} {8:<6} |"
        row_format = "| {0:<12} {1:<12} {2:<12} {3:>5} {4:>8} {5:>9} {6:>9} {7:>10} {8:>7}  |"

        print(header_format.format("Book IDs", "Name", "Type", "Ncopy","Maxday", "Lcharge", "Nborrow", "Nreserve", "Range"))
        print("-" * 97)

        textbook_list = []
        for book in self.books.values():
            if isinstance(book, Textbook):
                textbook_list.append(book)
        textbook_list.sort(key=lambda x: x.name)  # Sort by name

        for book in textbook_list:
            nborrow, nreserve, range_days = book.calculate()
            print(row_format.format(book.bookID, book.name, book.book_type, book.ncopy, book.maxday, book.lcharge, nborrow, nreserve, range_days))

        print("-" * 97)

        # Display fiction information
        print("\nFICTION INFORMATION")
        print("-" * 97)
        print(header_format.format("Book IDs", "Name", "Type", "Ncopy", "Maxday", "Lcharge", "Nborrow", "Nreserve", "Range"))
        print("-" * 97)

        fiction_list = []
        for book in self.books.values():
            if isinstance(book, Fiction):
                fiction_list.append(book)
        fiction_list.sort(key=lambda x: x.name)  # Sort by name

        for book in fiction_list:
            nborrow, nreserve, range_days = book.calculate()
            print(row_format.format(book.bookID, book.name, book.book_type, book.ncopy, book.maxday, book.lcharge, nborrow, nreserve, range_days))
        print("-" * 97)

        # Summary sentences
        most_popular_books = []
        Max_reserve_borrow = 0
        for book in self.books.values():
            nborrow, nreserve, range_days = book.calculate()
            if nreserve + nborrow > Max_reserve_borrow:
                Max_reserve_borrow = nreserve + nborrow
                most_popular_books = [book]
            elif nreserve + nborrow == Max_reserve_borrow:
                most_popular_books.append(book)

        longest_borrow = []
        max_borrow_days = 0
        for book in self.books.values():
            borrow_days = []
            for days in book.borrowed_days.values():
                if isinstance(days, int):
                    borrow_days.append(days)

            if len(borrow_days) > 0:
                Max_days = max(borrow_days)
            else:
                Max_days = 0
            if Max_days > max_borrow_days:
                max_borrow_days = Max_days
                longest_borrow = [book]
            elif Max_days == max_borrow_days:
                longest_borrow.append(book)

        if len(most_popular_books) > 0:
            popular_books = []
            for book in most_popular_books:
                popular_books.append(book.name)
            popular_books_list = ", ".join(popular_books)
            print(f"The most popular book(s): {popular_books_list}.")

        if len(longest_borrow) > 0:
            longest_borrow_books = []
            for book in longest_borrow:
                longest_borrow_books.append(book.name)
            longest_borrow_books_list = ", ".join(longest_borrow_books)
            print(f"The book(s) with the longest borrow days: {longest_borrow_books_list} ({max_borrow_days} days).\n")

    def display_members(self):

        standard_members = []
        premium_members = []

        for member in self.members.values():
            if isinstance(member, Standard):
                standard_members.append(member)
            elif isinstance(member, Premium):
                premium_members.append(member)

        # Sort standard members by fee in descending order
        standard_members.sort(key=lambda member: member.compute_fee(self.books), reverse=True)

        # Sort premium members by fee in descending order
        premium_members.sort(key=lambda member: member.compute_fee(self.books), reverse=True)

        # Display member information
        print("STANDARD MEMBER INFORMATION")
        print("-" * 107)
        header_format = "| {0:<12} {1:<12} {2:<12} {3:<12} {4:<12} {5:<11} {6:<10} {7:<9} {8:>5}  |"
        row_format = "| {0:<12} {1:<12} {2:<12} {3:<12} {4:<12} {5:>9} {6:>10} {7:>9.2f} {8:>8.2f} |"
        print(header_format.format("Member IDs", "FName", "LName", "Type", "DOB", "Ntextbook", "Nfiction", "Average", "Fee"))
        print("-" * 107)

        for member in standard_members:
            textbooks, fictions, avg_days = member.compute()
            dob_formatted = member.dob.strftime("%d-%b-%Y")
            fee = member.compute_fee(self.books)
            ntextbook_str = str(textbooks)
            nfiction_str = str(fictions)

            if textbooks > 1:
                ntextbook_str += "!"
            if fictions > 2:
                nfiction_str += "!"

            print(row_format.format(member.memberID, member.first_name, member.last_name, member.member_type, dob_formatted, ntextbook_str, nfiction_str, avg_days, fee))

        print("-" * 107)

        # Display premium members
        print("PREMIUM MEMBERS")
        print("-" * 107)
        header_format = "| {0:<12} {1:<12} {2:<12} {3:<12} {4:<12} {5:<11} {6:<10} {7:<9} {8:>5}  |"
        row_format = "| {0:<12} {1:<12} {2:<12} {3:<12} {4:<12} {5:>9} {6:>10} {7:>9.2f} {8:>8.2f} |"
        print(header_format.format("Member IDs", "FName", "LName", "Type", "DOB", "Ntextbook", "Nfiction", "Average", "Fee"))
        print("-" * 107)
        for member in premium_members:
            textbooks, fictions, avg_days = member.compute()
            dob_formatted = member.dob.strftime("%d-%b-%Y")
            fee = member.compute_fee(self.books)
            ntextbook_str = str(textbooks)
            nfiction_str = str(fictions)

            if textbooks > 2:
                ntextbook_str += "!"
            if fictions > 3:
                nfiction_str += "!"

            print(row_format.format(member.memberID, member.first_name, member.last_name,
                member.member_type, dob_formatted, ntextbook_str, nfiction_str, avg_days, fee))

        print("-" * 107)

        # Summary sentences
        most_active_members = []
        max_books_borrowed = 0
        min_avg_days = float('inf')
        least_days_member = []

        for member in self.members.values():
            textbooks, fictions, avg_days = member.compute()
            total_books = textbooks + fictions

            if total_books > max_books_borrowed:
                max_books_borrowed = total_books
                most_active_members = [member]
            elif total_books == max_books_borrowed:
                most_active_members.append(member)

            if avg_days < min_avg_days:
                min_avg_days = avg_days
                least_days_member = [member]
            elif avg_days == min_avg_days:
                least_days_member.append(member)

        if most_active_members:
            active_members_names_list = []
            for m in most_active_members:
                active_members_names_list.append(f"{m.first_name} {m.last_name}")
            active_members_names = ", ".join(active_members_names_list)
            print(f"The most active members are: {active_members_names} with {max_books_borrowed} books borrowed/reserved.")

        if least_days_member:
            least_avg_days_names_list = []
            for m in least_days_member:
                least_avg_days_names_list.append(f"{m.first_name} {m.last_name}")
            least_avg_days_names = ", ".join(least_avg_days_names_list)
            print(f"The member with the least average number of borrowing days is {least_avg_days_names} with {min_avg_days:.2f} days.\n")

    def save_books(self, file):
        # Save textbook information
        file.write("TEXTBOOK INFORMATION\n")
        file.write("-" * 97 + "\n")
        header_format = "| {0:<12} {1:<12} {2:<12} {3:<7} {4:<8} {5:<9} {6:<9} {7:<10} {8:<6} |\n"
        row_format = "| {0:<12} {1:<12} {2:<12} {3:>5} {4:>8} {5:>9} {6:>9} {7:>10} {8:>7}  |\n"
        file.write(header_format.format("Book IDs", "Name", "Type",
                "Ncopy", "Maxday", "Lcharge", "Nborrow", "Nreserve", "Range"))
        file.write("-" * 97 + "\n")

        textbook_list = []
        for book in self.books.values():
            if isinstance(book, Textbook):
                textbook_list.append(book)

        textbook_list.sort(key=lambda x: x.name)  # Sort by name

        for book in textbook_list:
            nborrow, nreserve, range_days = book.calculate()
            file.write(row_format.format(book.bookID, book.name, book.book_type,
                    book.ncopy, book.maxday, book.lcharge, nborrow, nreserve, range_days))

        file.write("-" * 97 + "\n")

        # Save fiction information
        file.write("FICTION INFORMATION\n")
        file.write("-" * 97 + "\n")
        file.write(header_format.format("Book IDs", "Name", "Type",
                "Ncopy", "Maxday", "Lcharge", "Nborrow", "Nreserve", "Range"))
        file.write("-" * 97 + "\n")

        fiction_list = []
        for book in self.books.values():
            if isinstance(book, Fiction):
                fiction_list.append(book)

        fiction_list.sort(key=lambda x: x.name)  # Sort by name

        for book in fiction_list:
            nborrow, nreserve, range_days = book.calculate()
            file.write(row_format.format(book.bookID, book.name, book.book_type,
                    book.ncopy, book.maxday, book.lcharge, nborrow, nreserve, range_days))

        file.write("-" * 97 + "\n")

        # Summary sentences
        most_popular_books = []
        Max_reserve_borrow = 0
        for book in self.books.values():
            nborrow, nreserve, range_days = book.calculate()
            if nreserve + nborrow > Max_reserve_borrow:
                Max_reserve_borrow = nreserve + nborrow
                most_popular_books = [book]
            elif nreserve + nborrow == Max_reserve_borrow:
                most_popular_books.append(book)

        longest_borrow = []
        max_borrow_days = 0
        for book in self.books.values():
            borrow_days = []
            for days in book.borrowed_days.values():
                if isinstance(days, int):
                    borrow_days.append(days)

            if len(borrow_days) > 0:
                Max_days = max(borrow_days)
            else:
                Max_days = 0
            if Max_days > max_borrow_days:
                max_borrow_days = Max_days
                longest_borrow = [book]
            elif Max_days == max_borrow_days:
                longest_borrow.append(book)

        if len(most_popular_books) > 0:
            popular_books = []
            for book in most_popular_books:
                popular_books.append(book.name)
            popular_books_list = ", ".join(popular_books)
            file.write(f"The most popular book(s): {popular_books_list}.")

        if len(longest_borrow) > 0:
            longest_borrow_books = []
            for book in longest_borrow:
                longest_borrow_books.append(book.name)
            longest_borrow_books_list = ", ".join(longest_borrow_books)
            file.write(f"The book(s) with the longest borrow days: {longest_borrow_books_list} ({max_borrow_days} days).\n\n")

    def save_members(self, file):
        file.write("STANDARD MEMBER INFORMATION\n")
        file.write("-" * 107 + "\n")
        header_format = "| {0:<12} {1:<12} {2:<12} {3:<12} {4:<12} {5:<11} {6:<10} {7:<9} {8:>5}  |\n"
        row_format = "| {0:<12} {1:<12} {2:<12} {3:<12} {4:<12} {5:>9} {6:>10} {7:>9.2f} {8:>8.2f} |\n"
        file.write(header_format.format("Member IDs", "FName", "LName", "Type", "DOB", "Ntextbook", "Nfiction", "Average", "Fee"))
        file.write("-" * 107 + "\n")

        standard_members = []
        premium_members = []

        for member in self.members.values():
            if isinstance(member, Standard):
                standard_members.append(member)
            elif isinstance(member, Premium):
                premium_members.append(member)

        standard_members.sort(
            key=lambda member: member.compute_fee(self.books), reverse=True)
        premium_members.sort(
            key=lambda member: member.compute_fee(self.books), reverse=True)


        for member in standard_members:
            textbooks, fictions, avg_days = member.compute()
            dob_formatted = member.dob.strftime("%d-%b-%Y")
            fee = member.compute_fee(self.books)
            ntextbook_str = str(textbooks)
            nfiction_str = str(fictions)

            if textbooks > 1:
                ntextbook_str += "!"
            if fictions > 2:
                nfiction_str += "!"

            file.write(row_format.format(member.memberID, member.first_name, member.last_name, member.member_type, dob_formatted, ntextbook_str, nfiction_str, avg_days, fee))

        file.write("-" * 107 + "\n")

        file.write("PREMIUM MEMBER INFORMATION\n")
        file.write("-" * 107 + "\n")
        file.write(header_format.format("Member IDs", "FName", "LName", "Type", "DOB", "Ntextbook", "Nfiction", "Average", "Fee"))
        file.write("-" * 107 + "\n")

        for member in premium_members:
            textbooks, fictions, avg_days = member.compute()
            dob_formatted = member.dob.strftime("%d-%b-%Y")
            fee = member.compute_fee(self.books)
            ntextbook_str = str(textbooks)
            nfiction_str = str(fictions)

            if textbooks > 2:
                ntextbook_str += "!"
            if fictions > 3:
                nfiction_str += "!"

            file.write(row_format.format(member.memberID, member.first_name, member.last_name, member.member_type, dob_formatted, ntextbook_str, nfiction_str, avg_days, fee))

        file.write("-" * 107 + "\n")

    def save_data(self, filename):
        try:
            file = open(filename, "a") # Open the file in append mode
            current_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            file.write("\n" + "▼" * 110 + "\n")
            file.write(f"★ Report generated on: {current_time}\n\n")
            self.save_books(file)
            if self.members_loaded:  # Check if member file was loaded
                self.save_members(file)
            file.write("\n" + "▲" * 110 + "\n")
        except Exception as e:
            print(e)
        finally:
            file.close()

class Main:
    def __init__(self, args):
        self.args = args

    def run(self):
        if len(self.args) == 2:
            record_file = self.args[1]
            record = Record()
            record.read_records(record_file)
            record.display_records()
        elif len(self.args) == 3:
            record_file = self.args[1]
            book_file = self.args[2]
            record = Record()
            record.read_books(book_file)
            record.read_records(record_file)
            record.display_records()
            record.display_books()
            record.save_data("reports.txt")
        elif len(self.args) == 4:
            record_file = self.args[1]
            book_file = self.args[2]
            member_file = self.args[3]
            record = Record()
            record.read_books(book_file)
            record.read_records(record_file)
            record.read_members(member_file)
            record.display_records()
            record.display_books()
            record.display_members()
            record.save_data("reports.txt")
        else:
            print("[Usage:] python my_record.py <record file> <book file>")
            return


class Program:
    @staticmethod
    def main():
        main_program = Main(sys.argv)
        main_program.run()


if __name__ == "__main__":
    Program.main()


# ################### The Overview and Design Process ####################
# This is a library management program that includes management of books, members, and borrowing records. When I designed the system, I created several key classes. The main classes include custom exception classes, book class, member class, and record class. The custom exception classes are used to handle specific errors. The Book class is to manage book attributes and days borrowed. The Member class is to manage member information and borrowing records. The Record class is used to read and save data. These classes work together through object-oriented design to provide a clear structure and easy-to-maintain code.

################### Main Classes ####################
# 1. Books Class
# Use this class to avoid code duplication and manage different types of books efficiently.
# Book: Basic attributes and methods for managing books.
# Textbook and Fiction: inherited from the Book category, with additional methods and attributes for specific types of books.

# 2. Member Class
# Use this class to avoid code redundancy and to manage different types of members efficiently.
# Member: Contains basic attributes and methods.
# Standard and Premium: inherited from the Member category, with additional methods and attributes specific types of members.

# 3. Record Class:
# This class encapsulates all data management tasks, simplifying data access and modification.
# Manage lists of books and members, and handle data reads and writes from files.

################### Function and Method Choices ####################

# 1. Customized Exceptions:
# To handle specific errors, I defined custom exceptions such as InvalidIDFormat, EmptyFile, InvalidResults, etc.
# Reason: Custom exceptions provide clear error messages and make debugging easier.

# 2. Data Type:
# Use dictionaries to store information about multiple books and members.
# Reason: Dictionaries provide a simple way to manage collections of items with efficient indexing and iterative abilities.

# 3. Main Functions:
# Use Main function to handle command line arguments and start the program.
# Reason: Main functions provide a clear entry point to the program, keep the code structure organized and easy to understand, and make it easier to debug and maintain the code.
