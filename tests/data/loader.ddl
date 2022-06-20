CREATE TABLE `temp_whzan_monthly_data` (
  `activity_month` text,
  `Caseload` text,
  `Caseload_Size` text,
  `Days_Since_Last_Reading` text,
  `BP` int DEFAULT NULL,
  `Pulse` int DEFAULT NULL,
  `O2` int DEFAULT NULL,
  `Temp` int DEFAULT NULL,
  `NEWS` int DEFAULT NULL,
  `NEWS2(0-4)` int DEFAULT NULL,
  `NEWS2(5-6)` int DEFAULT NULL,
  `NEWS2(7+)` int DEFAULT NULL,
  `NEWS2` int DEFAULT NULL,
  `Photos` text,
  `ECG` text,
  `Stethoscope` text,
  `Clients_With_Readings` int DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci
/
