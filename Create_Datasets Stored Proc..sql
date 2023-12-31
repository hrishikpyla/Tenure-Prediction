USE [INFINITE_ML]
GO
/****** Object:  StoredProcedure [dbo].[Create_Datasets]    Script Date: 11-07-2023 14:51:02 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


ALTER PROCEDURE [dbo].[Create_Datasets] (@client int)
AS
BEGIN
	set @client=CONVERT(varchar(10),@client);
	declare @myTable nvarchar(100);
	Set @myTable='dbo.trainingData';

	declare @sql nvarchar(MAX);

	--Creating a Tenure Column
	--set @sql=CONCAT('ALTER TABLE ',@myTable,' ADD tenure int;');
	--exec sp_executesql @sql;

	----setting the tenure value
	--set @sql=CONCAT('UPDATE ',@myTable,' SET Tenure = EndYear-StartYear WHERE (EndYear is not null AND StartYear is not null);');
	--exec sp_executesql @sql;
	
	--set @sql=CONCAT('ALTER TABLE ',@myTable,' DROP COLUMN StartYear;');
	--exec sp_executesql @sql;
	--set @sql=CONCAT('ALTER TABLE ',@myTable,' DROP COLUMN EndYear;');
	--exec sp_executesql @sql;

	--Collecting the applicants and their first job
	set @sql=CONCAT('SELECT ResumeKey as [Key],MAX(ExpSeq) as [MAX(ExpSeq)]
					INTO MaxExpSeq_Freshers 
                    FROM ',@myTable,' GROUP BY ResumeKey;');
	exec sp_executesql @sql;

	--Creating the dataset1 combining the MaxExpSeq_Freshers table and myTable
	set @sql=CONCAT('SELECT a.ResumeKey, a.ExpSeq AS ExpSeq1, a.OrgName AS OrgName1, a.Company_Tier AS Tier1, a.jobTitle AS Role1, a.[ONET Code] AS ONET_Code1, a.Tenure AS Tenure1 
					INTO DataSet1_',@client,'
					FROM ',@myTable,' AS a
					RIGHT JOIN dbo.MaxExpSeq_Freshers as b
					ON (a.ResumeKey=b.[Key] AND a.ExpSeq=b.[MAX(ExpSeq)])
					WHERE (a.Tenure IS NOT NULL AND a.Tenure>0 AND a.Tenure<50)
					ORDER BY ResumeKey');
	exec sp_executesql @sql;

	--deleting rows where Tiers and ONET_codes are NULL
	set @sql=CONCAT('DELETE FROM dbo.DataSet1_',@Client,'
					WHERE (Tier1 IS NULL OR ONET_Code1 IS NULL);');
	exec sp_executesql @sql;
	----------------------------- DATASET - 1 DONE -------------------------

	--Creating secondJobsOnly by taking max value - 1, which contains the list of applicants and their 2nd jobs only (for now)
	set @sql= CONCAT('SELECT a.ResumeKey, a.ExpSeq as ExpSeq2, a.OrgName AS OrgName2, a.Company_Tier AS Tier2, a.JobTitle AS Role2, a.[ONET Code] AS ONET_Code2, a.Tenure AS Tenure2
					INTO secondJobsOnly
					FROM ',@myTable,' AS a
					RIGHT JOIN dbo.MaxExpSeq_Freshers AS t
					on (a.ResumeKey=t.[Key] and a.ExpSeq=t.[MAX(ExpSeq)]-1)
					WHERE a.Tenure IS NOT NULL;');
	exec sp_executesql @sql;

	--Creating the final Dataset2 by combining dataset1 and secondJobsOnly
	set @sql= CONCAT('SELECT d2.ResumeKey, d1.OrgName1, d1.Tier1, d1.Role1, d1.ONET_Code1, d1.Tenure1, d1.ExpSeq1,
						d2.Orgname2, d2.Tier2, d2.Role2, d2.ONET_Code2, d2.Tenure2, d2.ExpSeq2
						INTO DataSet2_',@client,'
						FROM dbo.DataSet1_',@client,' as d1
						RIGHT JOIN dbo.secondJobsOnly as d2
						on (d2.ResumeKey=d1.ResumeKey)
						WHERE (d1.Tenure1 IS NOT NULL AND d2.Tenure2 IS NOT NULL AND d2.Tenure2>0 AND d2.Tenure2<50)
						ORDER BY d2.ResumeKey;');
	exec sp_executesql @sql;

	--deleting rows where Tiers and ONET_codes are NULL
	set @sql=CONCAT('DELETE FROM dbo.DataSet2_',@Client,'
					WHERE (Tier1 IS NULL OR ONET_Code1 IS NULL OR Tier2 IS NULL OR ONET_Code2 IS NULL);');
	exec sp_executesql @sql;

	-------------------------- DataSet - 2 DONE ---------------------------

	--Creating thirdJobsOnly by taking max value - 2, which contains the list of applicants and their 3rd jobs only (for now)
	set @sql=CONCAT('SELECT a.ResumeKey, a.ExpSeq as ExpSeq3, a.OrgName AS OrgName3, a.Company_Tier AS Tier3, a.JobTitle AS Role3, a.[ONET Code] AS ONET_Code3, a.Tenure AS Tenure3
						INTO thirdJobsOnly 
						FROM ',@myTable,' AS a
						RIGHT JOIN dbo.MaxExpSeq_Freshers AS t
						on (a.ResumeKey=t.[Key] and a.ExpSeq=t.[MAX(ExpSeq)]-2)
						WHERE a.Tenure IS NOT NULL;');
	exec sp_executesql @sql;

	--Creating the final Dataset3 by combining dataset2 and thirdJobsOnly
	set @sql= CONCAT('SELECT d3.ResumeKey, d2.OrgName1, d2.Tier1, d2.Role1, d2.ONET_Code1, d2.Tenure1,d2.ExpSeq1,
						d2.Orgname2, d2.Tier2, d2.Role2, d2.ONET_Code2, d2.Tenure2, d2.ExpSeq2,
						d3.OrgName3, d3.Tier3, d3.Role3, d3.ONET_Code3, d3.Tenure3, d3.ExpSeq3
						INTO DataSet3_',@Client,'
						FROM dbo.DataSet2_',@client,' as d2
						RIGHT JOIN dbo.thirdJobsOnly as d3
						on (d3.ResumeKey=d2.ResumeKey)
						WHERE (d2.Tenure1 IS NOT NULL AND d2.Tenure2 IS NOT NULL AND d3.Tenure3 IS NOT NULL AND d3.Tenure3>0 AND d3.Tenure3<50)
						ORDER BY d3.ResumeKey;');
	exec sp_executesql @sql;

	--deleting rows where Tiers and ONET_codes are NULL
	set @sql=CONCAT('DELETE FROM dbo.DataSet3_',@Client,'
					 WHERE (Tier1 IS NULL OR ONET_Code1 IS NULL OR Tier2 IS NULL OR ONET_Code2 IS NULL OR Tier3 IS NULL OR ONET_Code3 IS NULL);');
	exec sp_executesql @sql;
	-------------------------- DataSet - 3 DONE --------------------------

	--Creating fourthJobsOnly by taking max value - 3, which contains the list of applicants and their 4th jobs only (for now)
	set @sql=CONCAT('SELECT a.ResumeKey, a.ExpSeq as ExpSeq4, a.OrgName AS OrgName4, a.Company_Tier AS Tier4, a.JobTitle AS Role4, a.[ONET Code] AS ONET_Code4, a.Tenure AS Tenure4
						INTO fourthJobsOnly
						FROM ',@myTable,' AS a
						RIGHT JOIN dbo.MaxExpSeq_Freshers AS t
						on (a.ResumeKey=t.[Key] and a.ExpSeq=t.[MAX(ExpSeq)]-3)
						WHERE a.Tenure IS NOT NULL;');
	exec sp_executesql @sql;

	--Creating the final Dataset4 by combining dataset3 and fourthJobsOnly
	set @sql= CONCAT('SELECT d4.ResumeKey, d3.OrgName1, d3.Tier1, d3.Role1, d3.ONET_Code1, d3.Tenure1,d3.ExpSeq1,
						d3.Orgname2, d3.Tier2, d3.Role2, d3.ONET_Code2, d3.Tenure2, d3.ExpSeq2,
						d3.OrgName3, d3.Tier3, d3.Role3, d3.ONET_Code3, d3.Tenure3, d3.ExpSeq3,
						d4.OrgName4, d4.Tier4, d4.Role4, d4.ONET_Code4, d4.Tenure4, d4.ExpSeq4
						INTO DataSet4_',@client,'
						FROM dbo.DataSet3_',@Client,' as d3
						RIGHT JOIN dbo.fourthJobsOnly as d4
						on (d4.ResumeKey=d3.ResumeKey)
						WHERE (d3.Tenure1 IS NOT NULL AND d3.Tenure2 IS NOT NULL AND d3.Tenure3 IS NOT NULL AND d4.Tenure4 IS NOT NULL AND d4.Tenure4>0 AND d4.Tenure4<50)
						ORDER BY d4.ResumeKey;');
	exec sp_executesql @sql;

	--deleting rows where Tiers and ONET_codes are NULL
	set @sql=CONCAT('DELETE FROM dbo.DataSet4_',@Client,'
					WHERE (Tier1 IS NULL OR ONET_Code1 IS NULL OR Tier2 IS NULL OR ONET_Code2 IS NULL OR Tier3 IS NULL OR ONET_Code3 IS NULL OR Tier4 IS NULL OR ONET_Code4 IS NULL);');
	exec sp_executesql @sql;

	-------------------------- DataSet - 4 DONE --------------------------

	--Creating fifthJobsOnly by taking max value - 4, which contains the list of applicants and their 5th jobs only (for now)
	set @sql=CONCAT('SELECT a.ResumeKey, a.ExpSeq as ExpSeq5, a.OrgName AS OrgName5, a.Company_Tier AS Tier5, a.JobTitle AS Role5, a.[ONET Code] AS ONET_Code5, a.Tenure AS Tenure5
						INTO fifthJobsOnly
						FROM ',@myTable,' AS a
						RIGHT JOIN dbo.MaxExpSeq_Freshers AS t
						on (a.ResumeKey=t.[Key] and a.ExpSeq=t.[MAX(ExpSeq)]-4)
						WHERE a.Tenure IS NOT NULL;');
	exec sp_executesql @sql;

	--Creating the final Dataset5 by combining dataset4 and fifthJobsOnly
	set @sql=CONCAT('SELECT d5.ResumeKey, d4.OrgName1, d4.Tier1, d4.Role1, d4.ONET_Code1, d4.Tenure1, d4.ExpSeq1,
					d4.Orgname2, d4.Tier2, d4.Role2, d4.ONET_Code2, d4.Tenure2, d4.ExpSeq2,
					d4.OrgName3, d4.Tier3, d4.Role3, d4.ONET_Code3, d4.Tenure3, d4.ExpSeq3,
					d4.OrgName4, d4.Tier4, d4.Role4, d4.ONET_Code4, d4.Tenure4, d4.ExpSeq4,
					d5.OrgName5, d5.Tier5, d5.Role5, d5.ONET_Code5, d5.Tenure5, d5.ExpSeq5
					INTO DataSet5_',@Client,'
					FROM dbo.DataSet4_',@client,' as d4
					RIGHT JOIN dbo.fifthJobsOnly as d5
					on (d5.ResumeKey=d4.ResumeKey)
					WHERE (d4.Tenure1 IS NOT NULL AND d4.Tenure2 IS NOT NULL AND d4.Tenure3 IS NOT NULL AND d4.Tenure4 IS NOT NULL AND d5.Tenure5 IS NOT NULL AND d5.Tenure5>0 AND d5.Tenure5<50)
					ORDER BY d5.ResumeKey;');
	exec sp_executesql @sql;

	--deleting rows where Tiers and ONET_codes are NULL
	set @sql=CONCAT('DELETE FROM dbo.DataSet5_',@client,'
					WHERE (Tier1 IS NULL OR ONET_Code1 IS NULL OR Tier2 IS NULL OR ONET_Code2 IS NULL OR Tier3 IS NULL OR ONET_Code3 IS NULL OR Tier4 IS NULL OR ONET_Code4 IS NULL OR Tier5 IS NULL OR ONET_Code5 IS NULL);');
	exec sp_executesql @sql;
	---------------- DataSet - 5 DONE --------------------

	DROP TABLE dbo.fifthJobsOnly;
    DROP TABLE dbo.MaxExpSeq_Freshers;
    DROP TABLE dbo.secondJobsOnly;
    DROP TABLE dbo.fourthJobsOnly;
    DROP TABLE dbo.thirdJobsOnly;
END;

