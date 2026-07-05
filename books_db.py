BOOKS_DB = {
    "كيمياء عضوية": [
        {"title": "Organic Chemistry by Clayden", "author": "Jonathan Clayden", "year": "2001", "size": "35 MB", "ext": "pdf", "ia_id": "organicchemistry00clay_0"},
        {"title": "Organic Chemistry by McMurry", "author": "John E. McMurry", "year": "1984", "size": "28 MB", "ext": "pdf", "ia_id": "organicchemistry00john_0"},
        {"title": "Organic Chemistry by Carey", "author": "Francis A. Carey", "year": "1987", "size": "12 MB", "ext": "pdf", "ia_id": "organicchemistry0003care"},
        {"title": "March's Advanced Organic Chemistry", "author": "Michael Smith", "year": "2007", "size": "18 MB", "ext": "pdf", "ia_id": "marchsadvancedor00smit_424"},
    ],
    "كيمياء غير عضوية": [
        {"title": "Inorganic Chemistry by Shriver & Atkins", "author": "D. F. Shriver", "year": "1990", "size": "14 MB", "ext": "pdf", "ia_id": "inorganicchemist0000shri_l8j2"},
        {"title": "Advanced Inorganic Chemistry by Cotton", "author": "F. Albert Cotton", "year": "1962", "size": "20 MB", "ext": "pdf", "ia_id": "advancedinorgani04edcott_i1g7"},
        {"title": "Concepts and Models of Inorganic Chemistry", "author": "Bodie Eugene Douglas", "year": "1965", "size": "16 MB", "ext": "pdf", "ia_id": "conceptsmodelsof00doug"},
    ],
    "كيمياء فيزيائية": [
        {"title": "Physical Chemistry by Atkins", "author": "P. W. Atkins", "year": "2002", "size": "25 MB", "ext": "pdf", "ia_id": "atkinsphysicalch00pwat"},
        {"title": "Physical Chemistry by Levine", "author": "Ira N. Levine", "year": "1978", "size": "18 MB", "ext": "pdf", "ia_id": "physicalchemistr00levi_1"},
    ],
    "كيمياء تحليلية": [
        {"title": "Fundamentals of Analytical Chemistry by Skoog", "author": "Douglas A. Skoog", "year": "1963", "size": "20 MB", "ext": "pdf", "ia_id": "fundamentalsofan0000skoo_i1y4"},
        {"title": "Quantitative Chemical Analysis by Harris", "author": "Daniel C. Harris", "year": "2015", "size": "16 MB", "ext": "pdf", "ia_id": "quantitativechem00dani_1"},
        {"title": "Principles of Instrumental Analysis by Skoog", "author": "Douglas A. Skoog", "year": "1971", "size": "22 MB", "ext": "pdf", "ia_id": "principlesofinst0000unse_m2i8"},
    ],
    "كيمياء حيوية": [
        {"title": "Lehninger Principles of Biochemistry", "author": "Albert L. Lehninger", "year": "2000", "size": "30 MB", "ext": "pdf", "ia_id": "lehningerprincip00lehn_0"},
        {"title": "Fundamentals of Biochemistry by Voet & Voet", "author": "Donald Voet, Judith G. Voet", "year": "1999", "size": "28 MB", "ext": "pdf", "ia_id": "fundamentalsofbi0000voet_k8p4"},
    ],
    "كيمياء دوائية": [
        {"title": "Burger's Medicinal Chemistry", "author": "Alfred Burger", "year": "1951", "size": "30 MB", "ext": "pdf", "ia_id": "medicinalchemist0000burg"},
    ],
    "كيمياء بيئية": [
        {"title": "Environmental Chemistry by Baird", "author": "Colin Baird", "year": "1995", "size": "14 MB", "ext": "pdf", "ia_id": "environmentalche0000bair"},
        {"title": "Chemistry of the Environment by Spiro", "author": "Thomas G. Spiro", "year": "1996", "size": "11 MB", "ext": "pdf", "ia_id": "chemistryofenvir0000spir"},
    ],
    "كيمياء حرارية": [
        {"title": "Chemical Thermodynamics by Klotz", "author": "Irving M. Klotz", "year": "1950", "size": "10 MB", "ext": "pdf", "ia_id": "chemicalthermody00klot"},
    ],
    "كيمياء النانو": [
        {"title": "Nanochemistry: A Chemical Approach by Ozin", "author": "Geoffrey A. Ozin", "year": "2009", "size": "15 MB", "ext": "pdf", "ia_id": "nanochemistryche0000ozin_p1n4"},
    ],
    "كيمياء عامة": [
        {"title": "Chemistry: The Central Science", "author": "Theodore L. Brown", "year": "1977", "size": "32 MB", "ext": "pdf", "ia_id": "chemistrycentral00brow"},
        {"title": "General Chemistry by Petrucci", "author": "Ralph H. Petrucci", "year": "1972", "size": "28 MB", "ext": "pdf", "ia_id": "generalchemistry00petr"},
        {"title": "Principles of Modern Chemistry by Oxtoby", "author": "David W. Oxtoby", "year": "1986", "size": "20 MB", "ext": "pdf", "ia_id": "principlesofmode00oxto"},
    ],
}

ALL_BOOKS_FLAT = []
for branch, books in BOOKS_DB.items():
    for b in books:
        b["branch"] = branch
        ALL_BOOKS_FLAT.append(b)


def search_db(query):
    words = query.lower().split()
    results = []
    for book in ALL_BOOKS_FLAT:
        content = f"{book['title']} {book['author']} {book['branch']}".lower()
        if all(w in content for w in words):
            results.append(book)
    return results[:6]


def get_branch_books(branch_name):
    return BOOKS_DB.get(branch_name, [])
