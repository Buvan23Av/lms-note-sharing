// ============================================
// Neo4j Initialization Script for LMS
// ============================================
// Run this in the Neo4j Browser (http://localhost:7474)
// Or it will be executed by the XML importer
//
// MERGE = Create if not exists (idempotent - safe to run multiple times)
// This script creates the same data as the XML import,
// but can be used to set up Neo4j independently.

// --- Constraints (run these first) ---
CREATE CONSTRAINT student_id_unique IF NOT EXISTS FOR (s:Student) REQUIRE s.studentId IS UNIQUE;
CREATE CONSTRAINT note_id_unique IF NOT EXISTS FOR (n:Note) REQUIRE n.noteId IS UNIQUE;
CREATE CONSTRAINT topic_id_unique IF NOT EXISTS FOR (t:Topic) REQUIRE t.topicId IS UNIQUE;
CREATE CONSTRAINT subject_id_unique IF NOT EXISTS FOR (s:Subject) REQUIRE s.subjectId IS UNIQUE;

// --- Subject Nodes ---
MERGE (sub1:Subject {subjectId: 'SUB101'}) SET sub1.name = 'Database Management Systems', sub1.code = 'CS501';
MERGE (sub2:Subject {subjectId: 'SUB102'}) SET sub2.name = 'Data Structures and Algorithms', sub2.code = 'CS301';
MERGE (sub3:Subject {subjectId: 'SUB103'}) SET sub3.name = 'Operating Systems', sub3.code = 'CS502';
MERGE (sub4:Subject {subjectId: 'SUB104'}) SET sub4.name = 'Computer Networks', sub4.code = 'CS601';
MERGE (sub5:Subject {subjectId: 'SUB105'}) SET sub5.name = 'Digital Signal Processing', sub5.code = 'EC501';

// --- Student Nodes ---
MERGE (s1:Student {studentId: 'S101'}) SET s1.name = 'Arun Kumar';
MERGE (s2:Student {studentId: 'S102'}) SET s2.name = 'Priya Sharma';
MERGE (s3:Student {studentId: 'S103'}) SET s3.name = 'Rahul Verma';
MERGE (s4:Student {studentId: 'S104'}) SET s4.name = 'Sneha Patel';
MERGE (s5:Student {studentId: 'S105'}) SET s5.name = 'Vikram Singh';

// --- Topic Nodes ---
// DBMS Topics
MERGE (t101:Topic {topicId: 'T101'}) SET t101.name = 'Normalization';
MERGE (t102:Topic {topicId: 'T102'}) SET t102.name = 'ER Model';
MERGE (t103:Topic {topicId: 'T103'}) SET t103.name = 'SQL Queries';
MERGE (t104:Topic {topicId: 'T104'}) SET t104.name = 'Transactions';
MERGE (t105:Topic {topicId: 'T105'}) SET t105.name = 'Indexing';
MERGE (t106:Topic {topicId: 'T106'}) SET t106.name = 'Functional Dependency';
// DSA Topics
MERGE (t201:Topic {topicId: 'T201'}) SET t201.name = 'Arrays and Linked Lists';
MERGE (t202:Topic {topicId: 'T202'}) SET t202.name = 'Trees and Graphs';
MERGE (t203:Topic {topicId: 'T203'}) SET t203.name = 'Sorting Algorithms';
MERGE (t204:Topic {topicId: 'T204'}) SET t204.name = 'Dynamic Programming';
// OS Topics
MERGE (t301:Topic {topicId: 'T301'}) SET t301.name = 'Process Management';
MERGE (t302:Topic {topicId: 'T302'}) SET t302.name = 'Memory Management';
MERGE (t303:Topic {topicId: 'T303'}) SET t303.name = 'Deadlocks';
// CN Topics
MERGE (t401:Topic {topicId: 'T401'}) SET t401.name = 'OSI Model';
MERGE (t402:Topic {topicId: 'T402'}) SET t402.name = 'TCP/IP Protocol';
// DSP Topics
MERGE (t501:Topic {topicId: 'T501'}) SET t501.name = 'Fourier Transform';

// --- Note Nodes ---
MERGE (n101:Note {noteId: 'N101'}) SET n101.title = 'DBMS Normalization Notes';
MERGE (n102:Note {noteId: 'N102'}) SET n102.title = 'Functional Dependency Explained';
MERGE (n103:Note {noteId: 'N103'}) SET n103.title = 'ER Diagrams - Complete Guide';
MERGE (n104:Note {noteId: 'N104'}) SET n104.title = 'SQL Queries Cheat Sheet';
MERGE (n105:Note {noteId: 'N105'}) SET n105.title = 'Transaction Management Notes';
MERGE (n106:Note {noteId: 'N106'}) SET n106.title = 'Indexing and B-Trees';
MERGE (n107:Note {noteId: 'N107'}) SET n107.title = 'Arrays and Linked Lists Basics';
MERGE (n108:Note {noteId: 'N108'}) SET n108.title = 'Trees and Graph Traversal';
MERGE (n109:Note {noteId: 'N109'}) SET n109.title = 'Sorting Algorithms Comparison';
MERGE (n110:Note {noteId: 'N110'}) SET n110.title = 'Dynamic Programming Patterns';
MERGE (n111:Note {noteId: 'N111'}) SET n111.title = 'Process Scheduling Algorithms';
MERGE (n112:Note {noteId: 'N112'}) SET n112.title = 'Virtual Memory and Paging';
MERGE (n113:Note {noteId: 'N113'}) SET n113.title = 'Deadlock Detection and Prevention';
MERGE (n114:Note {noteId: 'N114'}) SET n114.title = 'OSI Model - All 7 Layers';
MERGE (n115:Note {noteId: 'N115'}) SET n115.title = 'Fourier Transform Basics';

// --- PART_OF Relationships (Topic belongs to Subject) ---
MATCH (t:Topic {topicId: 'T101'}), (s:Subject {subjectId: 'SUB101'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T102'}), (s:Subject {subjectId: 'SUB101'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T103'}), (s:Subject {subjectId: 'SUB101'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T104'}), (s:Subject {subjectId: 'SUB101'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T105'}), (s:Subject {subjectId: 'SUB101'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T106'}), (s:Subject {subjectId: 'SUB101'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T201'}), (s:Subject {subjectId: 'SUB102'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T202'}), (s:Subject {subjectId: 'SUB102'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T203'}), (s:Subject {subjectId: 'SUB102'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T204'}), (s:Subject {subjectId: 'SUB102'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T301'}), (s:Subject {subjectId: 'SUB103'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T302'}), (s:Subject {subjectId: 'SUB103'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T303'}), (s:Subject {subjectId: 'SUB103'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T401'}), (s:Subject {subjectId: 'SUB104'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T402'}), (s:Subject {subjectId: 'SUB104'}) MERGE (t)-[:PART_OF]->(s);
MATCH (t:Topic {topicId: 'T501'}), (s:Subject {subjectId: 'SUB105'}) MERGE (t)-[:PART_OF]->(s);

// --- UPLOADED Relationships ---
MATCH (s:Student {studentId: 'S101'}), (n:Note {noteId: 'N101'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S101'}), (n:Note {noteId: 'N102'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S102'}), (n:Note {noteId: 'N103'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S102'}), (n:Note {noteId: 'N104'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S103'}), (n:Note {noteId: 'N105'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S103'}), (n:Note {noteId: 'N106'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S101'}), (n:Note {noteId: 'N107'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S102'}), (n:Note {noteId: 'N108'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S103'}), (n:Note {noteId: 'N109'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S105'}), (n:Note {noteId: 'N110'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S105'}), (n:Note {noteId: 'N111'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S104'}), (n:Note {noteId: 'N112'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S105'}), (n:Note {noteId: 'N113'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S104'}), (n:Note {noteId: 'N114'}) MERGE (s)-[:UPLOADED]->(n);
MATCH (s:Student {studentId: 'S104'}), (n:Note {noteId: 'N115'}) MERGE (s)-[:UPLOADED]->(n);

// --- ABOUT Relationships (Note is about a Topic) ---
MATCH (n:Note {noteId: 'N101'}), (t:Topic {topicId: 'T101'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N102'}), (t:Topic {topicId: 'T106'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N103'}), (t:Topic {topicId: 'T102'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N104'}), (t:Topic {topicId: 'T103'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N105'}), (t:Topic {topicId: 'T104'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N106'}), (t:Topic {topicId: 'T105'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N107'}), (t:Topic {topicId: 'T201'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N108'}), (t:Topic {topicId: 'T202'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N109'}), (t:Topic {topicId: 'T203'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N110'}), (t:Topic {topicId: 'T204'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N111'}), (t:Topic {topicId: 'T301'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N112'}), (t:Topic {topicId: 'T302'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N113'}), (t:Topic {topicId: 'T303'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N114'}), (t:Topic {topicId: 'T401'}) MERGE (n)-[:ABOUT]->(t);
MATCH (n:Note {noteId: 'N115'}), (t:Topic {topicId: 'T501'}) MERGE (n)-[:ABOUT]->(t);

// --- PREREQUISITE_OF Relationships ---
MATCH (t1:Topic {topicId: 'T106'}), (t2:Topic {topicId: 'T101'}) MERGE (t1)-[:PREREQUISITE_OF]->(t2);
MATCH (t1:Topic {topicId: 'T102'}), (t2:Topic {topicId: 'T103'}) MERGE (t1)-[:PREREQUISITE_OF]->(t2);
MATCH (t1:Topic {topicId: 'T103'}), (t2:Topic {topicId: 'T104'}) MERGE (t1)-[:PREREQUISITE_OF]->(t2);
MATCH (t1:Topic {topicId: 'T101'}), (t2:Topic {topicId: 'T105'}) MERGE (t1)-[:PREREQUISITE_OF]->(t2);
MATCH (t1:Topic {topicId: 'T201'}), (t2:Topic {topicId: 'T202'}) MERGE (t1)-[:PREREQUISITE_OF]->(t2);
MATCH (t1:Topic {topicId: 'T202'}), (t2:Topic {topicId: 'T203'}) MERGE (t1)-[:PREREQUISITE_OF]->(t2);
MATCH (t1:Topic {topicId: 'T203'}), (t2:Topic {topicId: 'T204'}) MERGE (t1)-[:PREREQUISITE_OF]->(t2);
MATCH (t1:Topic {topicId: 'T301'}), (t2:Topic {topicId: 'T303'}) MERGE (t1)-[:PREREQUISITE_OF]->(t2);
MATCH (t1:Topic {topicId: 'T301'}), (t2:Topic {topicId: 'T302'}) MERGE (t1)-[:PREREQUISITE_OF]->(t2);
MATCH (t1:Topic {topicId: 'T401'}), (t2:Topic {topicId: 'T402'}) MERGE (t1)-[:PREREQUISITE_OF]->(t2);

// --- RELATED_TO Relationships (between notes) ---
MATCH (n1:Note {noteId: 'N101'}), (n2:Note {noteId: 'N102'}) MERGE (n1)-[:RELATED_TO]->(n2);
MATCH (n1:Note {noteId: 'N102'}), (n2:Note {noteId: 'N103'}) MERGE (n1)-[:RELATED_TO]->(n2);
MATCH (n1:Note {noteId: 'N103'}), (n2:Note {noteId: 'N104'}) MERGE (n1)-[:RELATED_TO]->(n2);
MATCH (n1:Note {noteId: 'N104'}), (n2:Note {noteId: 'N105'}) MERGE (n1)-[:RELATED_TO]->(n2);
MATCH (n1:Note {noteId: 'N105'}), (n2:Note {noteId: 'N106'}) MERGE (n1)-[:RELATED_TO]->(n2);
MATCH (n1:Note {noteId: 'N101'}), (n2:Note {noteId: 'N106'}) MERGE (n1)-[:RELATED_TO]->(n2);
MATCH (n1:Note {noteId: 'N107'}), (n2:Note {noteId: 'N108'}) MERGE (n1)-[:RELATED_TO]->(n2);
MATCH (n1:Note {noteId: 'N108'}), (n2:Note {noteId: 'N109'}) MERGE (n1)-[:RELATED_TO]->(n2);
MATCH (n1:Note {noteId: 'N109'}), (n2:Note {noteId: 'N110'}) MERGE (n1)-[:RELATED_TO]->(n2);
MATCH (n1:Note {noteId: 'N111'}), (n2:Note {noteId: 'N113'}) MERGE (n1)-[:RELATED_TO]->(n2);
MATCH (n1:Note {noteId: 'N111'}), (n2:Note {noteId: 'N112'}) MERGE (n1)-[:RELATED_TO]->(n2);

// --- FOLLOWS Relationships ---
MATCH (s1:Student {studentId: 'S101'}), (s2:Student {studentId: 'S102'}) MERGE (s1)-[:FOLLOWS]->(s2);
MATCH (s1:Student {studentId: 'S101'}), (s2:Student {studentId: 'S103'}) MERGE (s1)-[:FOLLOWS]->(s2);
MATCH (s1:Student {studentId: 'S102'}), (s2:Student {studentId: 'S101'}) MERGE (s1)-[:FOLLOWS]->(s2);
MATCH (s1:Student {studentId: 'S102'}), (s2:Student {studentId: 'S105'}) MERGE (s1)-[:FOLLOWS]->(s2);
MATCH (s1:Student {studentId: 'S103'}), (s2:Student {studentId: 'S101'}) MERGE (s1)-[:FOLLOWS]->(s2);
MATCH (s1:Student {studentId: 'S104'}), (s2:Student {studentId: 'S102'}) MERGE (s1)-[:FOLLOWS]->(s2);
MATCH (s1:Student {studentId: 'S105'}), (s2:Student {studentId: 'S101'}) MERGE (s1)-[:FOLLOWS]->(s2);
MATCH (s1:Student {studentId: 'S105'}), (s2:Student {studentId: 'S103'}) MERGE (s1)-[:FOLLOWS]->(s2);

// --- STUDIES Relationships ---
MATCH (s:Student {studentId: 'S101'}), (t:Topic {topicId: 'T101'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S101'}), (t:Topic {topicId: 'T102'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S101'}), (t:Topic {topicId: 'T106'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S101'}), (t:Topic {topicId: 'T201'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S102'}), (t:Topic {topicId: 'T102'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S102'}), (t:Topic {topicId: 'T103'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S102'}), (t:Topic {topicId: 'T202'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S103'}), (t:Topic {topicId: 'T104'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S103'}), (t:Topic {topicId: 'T203'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S103'}), (t:Topic {topicId: 'T201'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S104'}), (t:Topic {topicId: 'T302'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S104'}), (t:Topic {topicId: 'T401'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S104'}), (t:Topic {topicId: 'T501'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S105'}), (t:Topic {topicId: 'T204'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S105'}), (t:Topic {topicId: 'T301'}) MERGE (s)-[:STUDIES]->(t);
MATCH (s:Student {studentId: 'S105'}), (t:Topic {topicId: 'T303'}) MERGE (s)-[:STUDIES]->(t);

// --- LIKED Relationships ---
MATCH (s:Student {studentId: 'S101'}), (n:Note {noteId: 'N103'}) MERGE (s)-[:LIKED]->(n);
MATCH (s:Student {studentId: 'S101'}), (n:Note {noteId: 'N104'}) MERGE (s)-[:LIKED]->(n);
MATCH (s:Student {studentId: 'S101'}), (n:Note {noteId: 'N108'}) MERGE (s)-[:LIKED]->(n);
MATCH (s:Student {studentId: 'S102'}), (n:Note {noteId: 'N101'}) MERGE (s)-[:LIKED]->(n);
MATCH (s:Student {studentId: 'S102'}), (n:Note {noteId: 'N102'}) MERGE (s)-[:LIKED]->(n);
MATCH (s:Student {studentId: 'S102'}), (n:Note {noteId: 'N107'}) MERGE (s)-[:LIKED]->(n);
MATCH (s:Student {studentId: 'S103'}), (n:Note {noteId: 'N101'}) MERGE (s)-[:LIKED]->(n);
MATCH (s:Student {studentId: 'S103'}), (n:Note {noteId: 'N108'}) MERGE (s)-[:LIKED]->(n);
MATCH (s:Student {studentId: 'S104'}), (n:Note {noteId: 'N111'}) MERGE (s)-[:LIKED]->(n);
MATCH (s:Student {studentId: 'S104'}), (n:Note {noteId: 'N113'}) MERGE (s)-[:LIKED]->(n);
MATCH (s:Student {studentId: 'S105'}), (n:Note {noteId: 'N101'}) MERGE (s)-[:LIKED]->(n);
MATCH (s:Student {studentId: 'S105'}), (n:Note {noteId: 'N109'}) MERGE (s)-[:LIKED]->(n);

// --- BOOKMARKED Relationships ---
MATCH (s:Student {studentId: 'S101'}), (n:Note {noteId: 'N101'}) MERGE (s)-[:BOOKMARKED]->(n);
MATCH (s:Student {studentId: 'S101'}), (n:Note {noteId: 'N102'}) MERGE (s)-[:BOOKMARKED]->(n);
MATCH (s:Student {studentId: 'S101'}), (n:Note {noteId: 'N107'}) MERGE (s)-[:BOOKMARKED]->(n);
MATCH (s:Student {studentId: 'S102'}), (n:Note {noteId: 'N103'}) MERGE (s)-[:BOOKMARKED]->(n);
MATCH (s:Student {studentId: 'S102'}), (n:Note {noteId: 'N104'}) MERGE (s)-[:BOOKMARKED]->(n);
MATCH (s:Student {studentId: 'S103'}), (n:Note {noteId: 'N105'}) MERGE (s)-[:BOOKMARKED]->(n);
MATCH (s:Student {studentId: 'S103'}), (n:Note {noteId: 'N109'}) MERGE (s)-[:BOOKMARKED]->(n);
MATCH (s:Student {studentId: 'S104'}), (n:Note {noteId: 'N112'}) MERGE (s)-[:BOOKMARKED]->(n);
MATCH (s:Student {studentId: 'S104'}), (n:Note {noteId: 'N114'}) MERGE (s)-[:BOOKMARKED]->(n);
MATCH (s:Student {studentId: 'S105'}), (n:Note {noteId: 'N110'}) MERGE (s)-[:BOOKMARKED]->(n);
MATCH (s:Student {studentId: 'S105'}), (n:Note {noteId: 'N111'}) MERGE (s)-[:BOOKMARKED]->(n);
