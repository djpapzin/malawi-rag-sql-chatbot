import os
import csv
from datetime import datetime
import json
import sqlite3

class ResultHandler:
    def __init__(self, base_dir="results"):
        self.base_dir = base_dir
        self._ensure_directories()
        self.column_names = self._get_column_names()
    
    def _ensure_directories(self):
        """Ensure the results directories exist"""
        os.makedirs(self.base_dir, exist_ok=True)
        
    def _get_column_names(self):
        """Get column names from the database"""
        try:
            conn = sqlite3.connect('malawi_projects1.db')
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM proj_dashboard LIMIT 1")
            names = [description[0] for description in cursor.description]
            conn.close()
            return names
        except Exception as e:
            print(f"Error getting column names: {e}")
            return None

    def _generate_filename(self, prefix="query"):
        """Generate a unique filename based on timestamp"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return f"{prefix}_{timestamp}"
    
    def _format_result_for_csv(self, result):
        """Format the result for CSV saving"""
        if isinstance(result, str):
            try:
                result = eval(result)  # Safely convert string representation of tuple/list to actual data
            except:
                return [{"Result": result}]
        
        if isinstance(result, list) and len(result) > 0:
            if isinstance(result[0], tuple):
                # Get the actual column names from the SQL query
                columns = [
                    'PROJECTNAME', 'PROJECTCODE', 'FISCALYEAR', 'REGION', 'DISTRICT',
                    'TOTALBUDGET', 'PROJECTSTATUS', 'PROJECTSECTOR', 'CONTRACTORNAME',
                    'STARTDATE', 'TOTALEXPENDITURETODATE', 'FUNDINGSOURCE', 'LASTVISIT'
                ]
                
                # Create list of dictionaries with proper column names
                formatted_data = []
                for row in result:
                    row_dict = {}
                    for i, value in enumerate(row):
                        if i < len(columns):
                            # Use the actual column name
                            col_name = columns[i]
                            # Format the value
                            if value is None:
                                row_dict[col_name] = "N/A"
                            elif isinstance(value, (int, float)):
                                if col_name == 'TOTALBUDGET':
                                    row_dict[col_name] = f"MWK {value:,}"
                                elif col_name == 'COMPLETIONPERCENTAGE':
                                    row_dict[col_name] = f"{value}%"
                                else:
                                    row_dict[col_name] = f"{value:,}"
                            else:
                                row_dict[col_name] = str(value)
                    formatted_data.append(row_dict)
                return formatted_data
            elif isinstance(result[0], dict):
                return result
        
        return [{"Result": str(result)}]

    def _format_result_for_markdown(self, result):
        """Format the result for markdown table"""
        if not result:
            return "No results found."
        
        if isinstance(result, str):
            try:
                result = eval(result)  # Safely convert string representation to actual data
            except:
                return f"```\n{result}\n```"
        
        if isinstance(result, list):
            if len(result) == 1 and isinstance(result[0], tuple) and len(result[0]) == 1:
                # Single value result (e.g., COUNT or SUM)
                return str(result[0][0])
            
            if isinstance(result[0], tuple):
                # Get column names from database or use default list
                columns = self.column_names if self.column_names else [
                    'PROJECTNAME', 'PROJECTCODE', 'FISCALYEAR', 'REGION', 'DISTRICT',
                    'TOTALBUDGET', 'PROJECTSTATUS', 'PROJECTSECTOR', 'CONTRACTORNAME',
                    'STARTDATE', 'TOTALEXPENDITURETODATE', 'FUNDINGSOURCE', 'LASTVISIT'
                ]
                
                # Ensure we have enough column names for all values
                while len(columns) < len(result[0]):
                    columns.append(f"Column_{len(columns)}")
                
                # Create table header
                table = "| " + " | ".join(columns[:len(result[0])]) + " |\n"
                table += "| " + " | ".join(["---" for _ in range(len(result[0]))]) + " |\n"
                
                # Add data rows
                for row in result:
                    formatted_row = []
                    for i, value in enumerate(row):
                        if value is None:
                            formatted_row.append("")  # Empty string instead of N/A
                        elif isinstance(value, (int, float)):
                            if columns[i] == 'TOTALBUDGET':
                                formatted_row.append(f"MWK {value:,}")
                            elif columns[i] == 'COMPLETIONPERCENTAGE':
                                formatted_row.append(f"{value}%")
                            else:
                                formatted_row.append(f"{value:,}")
                        else:
                            formatted_row.append(str(value))
                    table += "| " + " | ".join(formatted_row) + " |\n"
                
                return table
            elif isinstance(result[0], dict):
                # Handle dictionary results
                columns = list(result[0].keys())
                table = "| " + " | ".join(columns) + " |\n"
                table += "| " + " | ".join(["---" for _ in columns]) + " |\n"
                
                for row in result:
                    formatted_row = []
                    for col in columns:
                        value = row.get(col)
                        if value is None:
                            formatted_row.append("")
                        elif isinstance(value, (int, float)):
                            if col == 'TOTALBUDGET':
                                formatted_row.append(f"MWK {value:,}")
                            elif col == 'COMPLETIONPERCENTAGE':
                                formatted_row.append(f"{value}%")
                            else:
                                formatted_row.append(f"{value:,}")
                        else:
                            formatted_row.append(str(value))
                    table += "| " + " | ".join(formatted_row) + " |\n"
                
                return table
        
        return f"```\n{str(result)}\n```"

    def _format_markdown_table(self, results, column_names=None):
        if not results:
            return "No results found."
        
        # Get column names from the database if not provided
        if not column_names:
            column_names = self._get_column_names()
        
        # Handle single value results (e.g., COUNT, SUM)
        if isinstance(results[0], (int, float)) or (isinstance(results[0], tuple) and len(results[0]) == 1):
            return str(results[0] if isinstance(results[0], (int, float)) else results[0][0])
        
        # Format column headers
        headers = []
        alignments = []
        for col in column_names:
            headers.append(str(col))
            alignments.append("---")  # Default center alignment
        
        # Create table header
        table = f"| {' | '.join(headers)} |\n| {' | '.join(alignments)} |"
        
        # Format and add each row
        for row in results:
            formatted_row = []
            for value in row:
                if value is None:
                    formatted_row.append("N/A")
                elif isinstance(value, (int, float)):
                    formatted_row.append(f"{value:,}")  # Add thousand separators
                else:
                    formatted_row.append(str(value))
            table += f"\n| {' | '.join(formatted_row)} |"
        
        return table

    def _save_json(self, filename, query, results, answer, natural_query=None):
        """Save results in JSON format"""
        try:
            data = {
                "question": natural_query if natural_query else "",
                "sql_query": query,
                "results": results,
                "answer": answer,
                "metadata": {
                    "generated_at": datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            }
            
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error saving JSON: {e}")

    def save_results(self, query, results, answer, natural_query=None):
        """Save results in Markdown, CSV, and JSON formats"""
        base_filename = self._generate_filename()
        
        # Save as Markdown
        md_filename = os.path.join(self.base_dir, f"{base_filename}.md")
        self._save_markdown(md_filename, query, results, answer, natural_query)
        
        # Save as CSV
        csv_filename = os.path.join(self.base_dir, f"{base_filename}.csv")
        self._save_csv(csv_filename, results)
        
        # Save as JSON
        json_filename = os.path.join(self.base_dir, f"{base_filename}.json")
        self._save_json(json_filename, query, results, answer, natural_query)
        
        return {
            "markdown_file": md_filename,
            "csv_file": csv_filename,
            "json_file": json_filename
        }
    
    def _save_markdown(self, filename, query, results, answer, natural_query=None):
        """Save results in Markdown format"""
        with open(filename, 'w', encoding='utf-8') as f:
            # Write header
            f.write(f"# Query Results\n\n")
            
            # Write natural language query if provided
            if natural_query:
                f.write("## Question\n")
                f.write(f"{natural_query}\n\n")
            
            # Write SQL query
            f.write("## SQL Query\n")
            f.write(f"```sql\n{query}\n```\n\n")
            
            # Write results
            f.write("## Results\n")
            f.write(self._format_result_for_markdown(results))
            f.write("\n")
            
            # Write answer section
            f.write("\n## Answer\n")
            
            # Get column names from the query
            columns = get_column_names(query)
            
            # Format the answer section
            f.write(format_answer_section(results, columns))
            
            # Write metadata
            f.write("\n## Metadata\n")
            f.write(f"- Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    def _save_csv(self, filename, results):
        """Save results in CSV format"""
        try:
            data = self._format_result_for_csv(results)
            
            if data:
                with open(filename, 'w', newline='', encoding='utf-8') as f:
                    writer = csv.DictWriter(f, fieldnames=data[0].keys())
                    writer.writeheader()
                    writer.writerows(data)
        except Exception as e:
            print(f"Error saving CSV: {e}")

def format_value(value, field_name):
    if value is None or value == "":
        return ""
    if "BUDGET" in field_name or "EXPENDITURE" in field_name:
        try:
            val = float(value)
            if val == 0:
                return ""
            return f"MWK {int(val):,}"
        except (ValueError, TypeError):
            return ""
    return str(value)

def format_answer_value(value, field_name, row=None, columns=None):
    if value is None or value == "" or value == "None":
        return "Not available"
    
    # Special handling for certain fields
    if "BUDGET" in field_name or "EXPENDITURE" in field_name:
        try:
            val = float(value)
            if val == 0:
                return "Not available"
            return f"MWK {int(val):,}"
        except (ValueError, TypeError):
            return "Not available"
    elif field_name == "REGION" and columns and "DISTRICT" in columns:
        district_idx = columns.index("DISTRICT")
        district = row[district_idx] if row[district_idx] else "Unknown District"
        return f"{value}, {district}"
    
    return str(value)

def create_markdown_table(columns, data):
    if not data:
        return "No results found.\n"
    
    # Create header
    table = "| " + " | ".join(columns) + " |\n"
    table += "| " + " | ".join(["---"] * len(columns)) + " |\n"
    
    # Add rows
    for row in data:
        formatted_values = [format_value(val, col) for val, col in zip(row[:len(columns)], columns)]
        table += "| " + " | ".join(formatted_values) + " |\n"
    
    return table

def format_answer_section(result, columns):
    """Format the answer section of the response"""
    if not result:
        return "No results found.\n"
    
    # Check if this is a single-project query
    is_single_project = any(col in columns for col in ["PROJECTNAME", "PROJECTCODE"]) and len(result) == 1
    
    if is_single_project:  # Single project
        row = result[0]
        field_order = [
            ("PROJECTNAME", "Project Name"),
            ("FISCALYEAR", "Fiscal Year"),
            ("REGION", "Location"),  # Changed to combine Region and District
            ("TOTALBUDGET", "Total Budget"),
            ("PROJECTSTATUS", "Project Status"),
            ("PROJECTSECTOR", "Project Sector"),
            ("CONTRACTORNAME", "Contractor"),
            ("STARTDATE", "Start Date"),
            ("TOTALEXPENDITURETODATE", "Total Expenditure"),
            ("FUNDINGSOURCE", "Funding Source"),
            ("PROJECTCODE", "Project Code"),
            ("LASTVISIT", "Last Visit")
        ]
        
        # Create a dictionary of column indices
        col_indices = {col: idx for idx, col in enumerate(columns)}
        
        # Format each field
        formatted_fields = []
        for db_field, display_name in field_order:
            if db_field in col_indices:
                idx = col_indices[db_field]
                if idx < len(row):  # Check if index is within bounds
                    value = row[idx]
                    
                    # Special handling for location
                    if db_field == "REGION":
                        district_idx = col_indices.get("DISTRICT")
                        district = row[district_idx] if district_idx is not None and district_idx < len(row) else None
                        if value and district:
                            formatted_value = f"{value}, {district}"
                        elif value:
                            formatted_value = value
                        else:
                            formatted_value = "Not available"
                    else:
                        # Format other fields
                        if value is None or value == "":
                            formatted_value = "Not available"
                        elif "BUDGET" in db_field or "EXPENDITURE" in db_field:
                            try:
                                val = float(value)
                                formatted_value = f"MWK {int(val):,}" if val > 0 else "Not available"
                            except (ValueError, TypeError):
                                formatted_value = "Not available"
                        else:
                            formatted_value = str(value)
                    
                    formatted_fields.append(f"* **{display_name}**: {formatted_value}")
        
        return "\n".join(formatted_fields) + "\n"
                
    else:  # Multiple projects or aggregate results
        answer = []
        answer.append(f"* **Total Projects**: {len(result)}")
        
        # Calculate total budget if available
        if "TOTALBUDGET" in columns:
            idx = columns.index("TOTALBUDGET")
            total_budget = 0
            budget_count = 0
            for row in result:
                if idx < len(row):  # Check if index is within bounds
                    try:
                        if row[idx] is not None and row[idx] != "":
                            val = float(row[idx])
                            if val > 0:
                                total_budget += val
                                budget_count += 1
                    except (ValueError, TypeError):
                        continue
            
            if budget_count > 0:
                answer.append(f"* **Total Budget**: MWK {int(total_budget):,}")
                answer.append(f"* **Projects with Budget**: {budget_count} out of {len(result)}")
            else:
                answer.append("* **Total Budget**: Not available")
        
        # Add district breakdown
        if "DISTRICT" in columns:
            idx = columns.index("DISTRICT")
            districts = {}
            for row in result:
                if idx < len(row):  # Check if index is within bounds
                    district = row[idx]
                    if district:
                        districts[district] = districts.get(district, 0) + 1
            
            if districts:
                answer.append("\n* **District Breakdown**:")
                for district, count in sorted(districts.items()):
                    answer.append(f"  - {district}: {count} project{'s' if count > 1 else ''}")
        
        # Add fiscal year breakdown
        if "FISCALYEAR" in columns:
            idx = columns.index("FISCALYEAR")
            fiscal_years = {}
            for row in result:
                if idx < len(row):  # Check if index is within bounds
                    year = row[idx]
                    if year:
                        fiscal_years[year] = fiscal_years.get(year, 0) + 1
            
            if fiscal_years:
                answer.append("\n* **Fiscal Year Breakdown**:")
                for year, count in sorted(fiscal_years.items()):
                    answer.append(f"  - {year}: {count} project{'s' if count > 1 else ''}")
        
        # Add sector breakdown
        if "PROJECTSECTOR" in columns:
            idx = columns.index("PROJECTSECTOR")
            sectors = {}
            for row in result:
                if idx < len(row):  # Check if index is within bounds
                    sector = row[idx] if row[idx] else "Not specified"
                    sectors[sector] = sectors.get(sector, 0) + 1
            
            if sectors:
                answer.append("\n* **Sector Breakdown**:")
                for sector, count in sorted(sectors.items()):
                    answer.append(f"  - {sector}: {count} project{'s' if count > 1 else ''}")
        
        # Add status breakdown
        if "PROJECTSTATUS" in columns:
            idx = columns.index("PROJECTSTATUS")
            statuses = {}
            for row in result:
                if idx < len(row):  # Check if index is within bounds
                    status = row[idx] if row[idx] else "Not specified"
                    statuses[status] = statuses.get(status, 0) + 1
            
            if statuses:
                answer.append("\n* **Status Breakdown**:")
                for status, count in sorted(statuses.items()):
                    answer.append(f"  - {status}: {count} project{'s' if count > 1 else ''}")
        
        return "\n".join(answer) + "\n"

def get_column_names(sql_query):
    """Extract column names from SQL query"""
    if not sql_query or 'SELECT' not in sql_query.upper():
        return ['*']
        
    try:
        # Extract the part between SELECT and FROM
        select_part = sql_query.upper().split('FROM')[0].replace('SELECT', '').strip()
        
        # Handle * queries
        if '*' in select_part:
            return ['*']
            
        # Split on commas and clean up each column name
        columns = []
        for col in select_part.split(','):
            col = col.strip()
            
            # Handle COUNT, SUM and other aggregates with aliases
            if ' AS ' in col:
                alias = col.split(' AS ')[-1].strip()
                columns.append(alias.strip('"\''))
                continue
                
            # Handle table.column notation
            if '.' in col:
                col = col.split('.')[-1]
                
            # Remove any remaining parentheses and quotes
            col = col.strip('"\'').strip('()')
            
            # Skip empty columns
            if col and col != '*':
                columns.append(col)
        
        return columns if columns else ['*']
        
    except Exception as e:
        print(f"Error extracting column names: {e}")
        return ['*']

def handle_result(question, sql_query, result, timestamp):
    """Handle the query result and save to files"""
    try:
        # Create results directory if it doesn't exist
        if not os.path.exists("results"):
            os.makedirs("results")
            
        # Generate filenames with timestamp
        timestamp_str = timestamp.strftime("%Y%m%d_%H%M%S")
        md_filename = f"results/query_{timestamp_str}.md"
        csv_filename = f"results/query_{timestamp_str}.csv"
        
        # Get column names from the query
        columns = get_column_names(sql_query)
        
        # Format markdown content
        markdown_content = "# Query Results\n\n"
        
        # Add question section
        markdown_content += "## Question\n"
        markdown_content += f"{question}\n\n"
        
        # Add SQL query section
        markdown_content += "## SQL Query\n"
        markdown_content += "```sql\n"
        markdown_content += f"{sql_query}\n"
        markdown_content += "```\n\n"
        
        # Add results section
        markdown_content += "## Results\n"
        if isinstance(result, list):
            markdown_content += create_markdown_table(columns, result)
        else:
            markdown_content += str(result)
        markdown_content += "\n\n"
        
        # Add answer section
        markdown_content += "## Answer\n"
        markdown_content += format_answer_section(result, columns)
        markdown_content += "\n"
        
        # Add metadata section
        markdown_content += "## Metadata\n"
        markdown_content += f"- Generated: {timestamp.strftime('%Y-%m-%d %H:%M:%S')}\n"
        
        # Save markdown file
        with open(md_filename, "w", encoding="utf-8") as f:
            f.write(markdown_content)
        
        # Save CSV file
        if isinstance(result, list) and result:
            with open(csv_filename, "w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(columns)
                writer.writerows(result)
        
        return {
            "markdown_file": md_filename,
            "csv_file": csv_filename
        }
    except Exception as e:
        print(f"Error handling result: {e}")
        return {
            "error": str(e),
            "markdown_file": None,
            "csv_file": None
        } 