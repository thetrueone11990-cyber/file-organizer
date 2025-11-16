"""
core/template_manager.py
Manages folder structure templates with 20+ predefined templates
"""

from pathlib import Path
from typing import List, Dict

class TemplateManager:
    """Manages folder organization templates"""
    
    def __init__(self):
        self.templates = self.get_predefined_templates()
    
    def get_predefined_templates(self) -> List[Dict]:
        """Return list of all predefined folder templates"""
        return [
            # Personal Organization
            {
                'name': 'Personal Complete',
                'description': 'Complete personal file organization',
                'structure': [
                    'Documents/Personal/Tax Returns',
                    'Documents/Personal/Medical Records',
                    'Documents/Personal/Legal',
                    'Documents/Personal/Insurance',
                    'Documents/Personal/Receipts',
                    'Documents/Work/Projects',
                    'Documents/Work/Meetings',
                    'Documents/Work/Reports',
                    'Photos/2024/Family',
                    'Photos/2024/Travel',
                    'Photos/2024/Events',
                    'Photos/2025/Family',
                    'Photos/2025/Travel',
                    'Videos/Family',
                    'Videos/Travel',
                    'Downloads/Temp',
                    'Desktop/Active Projects',
                    'Desktop/Quick Access'
                ]
            },
            
            # Student Organization
            {
                'name': 'Student Complete',
                'description': 'Complete academic organization system',
                'structure': [
                    'School/Fall 2024/Math',
                    'School/Fall 2024/Science',
                    'School/Fall 2024/English',
                    'School/Fall 2024/History',
                    'School/Fall 2024/Electives',
                    'School/Spring 2025/Math',
                    'School/Spring 2025/Science',
                    'School/Spring 2025/English',
                    'School/Spring 2025/History',
                    'School/Spring 2025/Electives',
                    'School/Projects/Current',
                    'School/Projects/Completed',
                    'School/Research Papers',
                    'School/Study Materials',
                    'School/Textbooks',
                    'School/Notes',
                    'School/Assignments/To Submit',
                    'School/Assignments/Graded',
                    'School/Exams/Practice',
                    'School/Exams/Previous',
                    'Extracurricular/Clubs',
                    'Extracurricular/Sports',
                    'Extracurricular/Volunteer'
                ]
            },
            
            # Developer Organization
            {
                'name': 'Developer Workspace',
                'description': 'Software development file structure',
                'structure': [
                    'Projects/Active/Frontend',
                    'Projects/Active/Backend',
                    'Projects/Active/Mobile',
                    'Projects/Active/Data Science',
                    'Projects/Archived/2024',
                    'Projects/Archived/2023',
                    'Projects/Learning/Tutorials',
                    'Projects/Learning/Courses',
                    'Projects/Open Source',
                    'Code Snippets/Python',
                    'Code Snippets/JavaScript',
                    'Code Snippets/Java',
                    'Code Snippets/C++',
                    'Code Snippets/SQL',
                    'Documentation/API Docs',
                    'Documentation/Technical Specs',
                    'Documentation/README Templates',
                    'Resources/Design Assets',
                    'Resources/Icons',
                    'Resources/Fonts',
                    'Resources/Libraries',
                    'Testing/Test Data',
                    'Testing/Test Scripts',
                    'Databases/Backups',
                    'Databases/Schemas',
                    'DevOps/Docker',
                    'DevOps/CI-CD',
                    'DevOps/Scripts'
                ]
            },
            
            # Creative Professional
            {
                'name': 'Creative Pro',
                'description': 'For designers, artists, and content creators',
                'structure': [
                    'Projects/2025/Client Work',
                    'Projects/2025/Personal',
                    'Projects/2024/Client Work',
                    'Projects/2024/Personal',
                    'Assets/Images/Stock Photos',
                    'Assets/Images/Screenshots',
                    'Assets/Icons',
                    'Assets/Fonts',
                    'Assets/Textures',
                    'Assets/3D Models',
                    'Assets/Audio/Music',
                    'Assets/Audio/SFX',
                    'Assets/Video Footage',
                    'Templates/Photoshop',
                    'Templates/Illustrator',
                    'Templates/After Effects',
                    'Templates/Premiere Pro',
                    'Inspiration/Design',
                    'Inspiration/Color Palettes',
                    'Inspiration/Typography',
                    'Portfolio/Web',
                    'Portfolio/Print',
                    'Portfolio/Video',
                    'Client Files/Contracts',
                    'Client Files/Invoices',
                    'Client Files/Briefs',
                    'Tutorials/Software',
                    'Tutorials/Techniques'
                ]
            },
            
            # Business Professional
            {
                'name': 'Business Complete',
                'description': 'Complete business file organization',
                'structure': [
                    'Business/Financial/2024/Q1',
                    'Business/Financial/2024/Q2',
                    'Business/Financial/2024/Q3',
                    'Business/Financial/2024/Q4',
                    'Business/Financial/2025/Q1',
                    'Business/Financial/Invoices/Sent',
                    'Business/Financial/Invoices/Received',
                    'Business/Financial/Expenses',
                    'Business/Financial/Tax Documents',
                    'Business/Clients/Active',
                    'Business/Clients/Past',
                    'Business/Clients/Prospects',
                    'Business/Clients/Contacts',
                    'Business/Projects/2024',
                    'Business/Projects/2025',
                    'Business/Marketing/Campaigns',
                    'Business/Marketing/Social Media',
                    'Business/Marketing/Analytics',
                    'Business/Marketing/Content',
                    'Business/Legal/Contracts',
                    'Business/Legal/Licenses',
                    'Business/Legal/Compliance',
                    'Business/HR/Employees',
                    'Business/HR/Policies',
                    'Business/Operations/Procedures',
                    'Business/Operations/Inventory',
                    'Business/Strategy/Plans',
                    'Business/Strategy/Reports'
                ]
            },
            
            # Photography Organization
            {
                'name': 'Photography Pro',
                'description': 'Professional photography organization',
                'structure': [
                    'Raw Files/2024/January',
                    'Raw Files/2024/February',
                    'Raw Files/2024/March',
                    'Raw Files/2025/January',
                    'Raw Files/2025/February',
                    'Edited/Portfolio/Nature',
                    'Edited/Portfolio/Portrait',
                    'Edited/Portfolio/Wedding',
                    'Edited/Portfolio/Commercial',
                    'Edited/Client Work/2024',
                    'Edited/Client Work/2025',
                    'Exports/Web/Small',
                    'Exports/Web/Large',
                    'Exports/Print/High Res',
                    'Exports/Social Media',
                    'Presets/Lightroom',
                    'Presets/Photoshop',
                    'Client Galleries/Active',
                    'Client Galleries/Delivered',
                    'Stock Photos/Submitted',
                    'Stock Photos/Approved',
                    'Equipment/Manuals',
                    'Equipment/Receipts',
                    'Backup/Cloud Sync',
                    'Backup/External Drive'
                ]
            },
            
            # Video Production
            {
                'name': 'Video Production',
                'description': 'Video editing and production workflow',
                'structure': [
                    'Projects/2025/Active',
                    'Projects/2025/Completed',
                    'Projects/2024/Archive',
                    'Footage/A-Roll',
                    'Footage/B-Roll',
                    'Footage/Drone',
                    'Footage/Archive',
                    'Audio/Voice Over',
                    'Audio/Music',
                    'Audio/SFX',
                    'Graphics/Lower Thirds',
                    'Graphics/Transitions',
                    'Graphics/Titles',
                    'Graphics/Logos',
                    'Exports/YouTube/1080p',
                    'Exports/YouTube/4K',
                    'Exports/Instagram',
                    'Exports/TikTok',
                    'Exports/Client Delivery',
                    'Templates/Premiere',
                    'Templates/After Effects',
                    'Templates/DaVinci',
                    'Color Grading/LUTs',
                    'Color Grading/Presets',
                    'Scripts/Pre-Production',
                    'Scripts/Storyboards'
                ]
            },
            
            # Music Production
            {
                'name': 'Music Producer',
                'description': 'Music production and audio engineering',
                'structure': [
                    'Projects/Active/Tracks',
                    'Projects/Active/Albums',
                    'Projects/Completed/2024',
                    'Projects/Completed/2025',
                    'Samples/Drums',
                    'Samples/Bass',
                    'Samples/Synths',
                    'Samples/Vocals',
                    'Samples/FX',
                    'Loops/Drums',
                    'Loops/Melodic',
                    'Loops/Ambient',
                    'Presets/Synths',
                    'Presets/Effects',
                    'Presets/Mixing',
                    'Recordings/Vocals',
                    'Recordings/Instruments',
                    'Recordings/Raw',
                    'Exports/WAV',
                    'Exports/MP3',
                    'Exports/Stems',
                    'Masters/Released',
                    'Masters/Unreleased',
                    'References/Inspiration',
                    'References/Mixing',
                    'Client Work/Beats',
                    'Client Work/Mix & Master'
                ]
            },
            
            # Writer Organization
            {
                'name': 'Writer\'s Workshop',
                'description': 'For authors, bloggers, and content writers',
                'structure': [
                    'Writing/Novels/Work In Progress',
                    'Writing/Novels/Completed',
                    'Writing/Novels/Drafts',
                    'Writing/Short Stories/Published',
                    'Writing/Short Stories/Drafts',
                    'Writing/Articles/Published',
                    'Writing/Articles/Drafts',
                    'Writing/Blog Posts/2024',
                    'Writing/Blog Posts/2025',
                    'Writing/Scripts/Theater',
                    'Writing/Scripts/Film',
                    'Writing/Poetry',
                    'Research/Books',
                    'Research/Articles',
                    'Research/Interviews',
                    'Research/Notes',
                    'Character Development',
                    'Plot Outlines',
                    'World Building',
                    'Publishing/Query Letters',
                    'Publishing/Submissions',
                    'Publishing/Contracts',
                    'Publishing/Marketing',
                    'Ideas/Concepts',
                    'Ideas/Prompts',
                    'Editing/First Draft',
                    'Editing/Revisions',
                    'Backup/Daily',
                    'Backup/Weekly'
                ]
            },
            
            # Research Academic
            {
                'name': 'Research Academic',
                'description': 'Academic research organization',
                'structure': [
                    'Research/Current Projects/Project A',
                    'Research/Current Projects/Project B',
                    'Research/Completed/2024',
                    'Research/Completed/2023',
                    'Literature Review/Papers',
                    'Literature Review/Books',
                    'Literature Review/Notes',
                    'Data/Raw Data',
                    'Data/Processed Data',
                    'Data/Analysis',
                    'Data/Backups',
                    'Papers/Drafts/In Progress',
                    'Papers/Submitted',
                    'Papers/Published',
                    'Papers/Rejected',
                    'Presentations/Conferences',
                    'Presentations/Seminars',
                    'Presentations/Lectures',
                    'Grants/Proposals',
                    'Grants/Awards',
                    'Grants/Reports',
                    'Teaching/Courses/Fall 2024',
                    'Teaching/Courses/Spring 2025',
                    'Teaching/Materials',
                    'Teaching/Assignments',
                    'Lab Notes/2024',
                    'Lab Notes/2025',
                    'Protocols',
                    'Collaboration/Shared Files'
                ]
            },
            
            # Minimalist
            {
                'name': 'Minimalist',
                'description': 'Simple, clean organization',
                'structure': [
                    'Work',
                    'Personal',
                    'Projects',
                    'Archive',
                    'Temp'
                ]
            },
            
            # Downloads Organizer
            {
                'name': 'Downloads Manager',
                'description': 'Organize messy downloads folder',
                'structure': [
                    'Downloads/Documents/PDFs',
                    'Downloads/Documents/Word',
                    'Downloads/Documents/Excel',
                    'Downloads/Images/Photos',
                    'Downloads/Images/Screenshots',
                    'Downloads/Videos',
                    'Downloads/Music',
                    'Downloads/Software/Installers',
                    'Downloads/Software/Portable',
                    'Downloads/Archives/ZIP',
                    'Downloads/Archives/RAR',
                    'Downloads/Temp/To Sort',
                    'Downloads/Temp/To Delete'
                ]
            },
            
            # Desktop Cleanup
            {
                'name': 'Desktop Organizer',
                'description': 'Clean desktop organization',
                'structure': [
                    'Desktop/Active Projects',
                    'Desktop/Quick Access',
                    'Desktop/To File',
                    'Desktop/Shortcuts',
                    'Desktop/Temp/Screenshots',
                    'Desktop/Temp/Downloads'
                ]
            },
            
            # Gaming Organization
            {
                'name': 'Gaming Setup',
                'description': 'For gamers and streamers',
                'structure': [
                    'Games/Screenshots/Game 1',
                    'Games/Screenshots/Game 2',
                    'Games/Videos/Highlights',
                    'Games/Videos/Full Games',
                    'Games/Mods/Installed',
                    'Games/Mods/Downloaded',
                    'Games/Saves/Backups',
                    'Games/Saves/Cloud',
                    'Streaming/Overlays',
                    'Streaming/Alerts',
                    'Streaming/Music',
                    'Streaming/Clips',
                    'Content/YouTube',
                    'Content/Twitch',
                    'Content/TikTok',
                    'Content/Thumbnails'
                ]
            },
            
            # Fitness & Health
            {
                'name': 'Fitness Tracker',
                'description': 'Health and fitness organization',
                'structure': [
                    'Fitness/Workout Plans/Current',
                    'Fitness/Workout Plans/Archive',
                    'Fitness/Progress Photos/2024',
                    'Fitness/Progress Photos/2025',
                    'Fitness/Meal Plans',
                    'Fitness/Recipes',
                    'Fitness/Tracking/Weight',
                    'Fitness/Tracking/Measurements',
                    'Health/Medical Records',
                    'Health/Lab Results',
                    'Health/Prescriptions',
                    'Health/Insurance'
                ]
            },
            
            # Travel Planner
            {
                'name': 'Travel Organizer',
                'description': 'Travel planning and memories',
                'structure': [
                    'Travel/Upcoming/Trip 1',
                    'Travel/Upcoming/Trip 2',
                    'Travel/Past/2024',
                    'Travel/Past/2023',
                    'Travel/Itineraries',
                    'Travel/Bookings/Flights',
                    'Travel/Bookings/Hotels',
                    'Travel/Bookings/Activities',
                    'Travel/Documents/Passports',
                    'Travel/Documents/Visas',
                    'Travel/Photos/2024',
                    'Travel/Photos/2025',
                    'Travel/Maps & Guides',
                    'Travel/Budget'
                ]
            },
            
            # Home Management
            {
                'name': 'Home Manager',
                'description': 'Complete home organization',
                'structure': [
                    'Home/Maintenance/Appliances',
                    'Home/Maintenance/HVAC',
                    'Home/Maintenance/Plumbing',
                    'Home/Maintenance/Electrical',
                    'Home/Warranties',
                    'Home/Manuals',
                    'Home/Repairs/Completed',
                    'Home/Repairs/Scheduled',
                    'Home/Improvements/Plans',
                    'Home/Improvements/Completed',
                    'Home/Bills/Utilities',
                    'Home/Bills/Insurance',
                    'Home/Bills/Mortgage',
                    'Home/Inventory',
                    'Home/Floor Plans'
                ]
            },
            
            # Event Planning
            {
                'name': 'Event Planner',
                'description': 'Event organization system',
                'structure': [
                    'Events/Upcoming/Event 1',
                    'Events/Upcoming/Event 2',
                    'Events/Past/2024',
                    'Events/Past/2023',
                    'Events/Vendors/Caterers',
                    'Events/Vendors/Venues',
                    'Events/Vendors/Decorators',
                    'Events/Budget/Quotes',
                    'Events/Budget/Invoices',
                    'Events/Guest Lists',
                    'Events/Invitations',
                    'Events/Decorations/Ideas',
                    'Events/Decorations/Purchased',
                    'Events/Photos/Professional',
                    'Events/Photos/Guest Photos'
                ]
            },
            
            # Freelancer Hub
            {
                'name': 'Freelancer Pro',
                'description': 'Freelance business organization',
                'structure': [
                    'Clients/Active/Client A',
                    'Clients/Active/Client B',
                    'Clients/Past',
                    'Clients/Prospects',
                    'Projects/Current',
                    'Projects/Completed/2024',
                    'Projects/Completed/2025',
                    'Invoices/Sent/2024',
                    'Invoices/Sent/2025',
                    'Invoices/Paid',
                    'Invoices/Pending',
                    'Contracts/Templates',
                    'Contracts/Signed',
                    'Expenses/2024',
                    'Expenses/2025',
                    'Taxes/2024',
                    'Taxes/2025',
                    'Marketing/Portfolio',
                    'Marketing/Social Media',
                    'Marketing/Website',
                    'Time Tracking',
                    'Templates/Proposals',
                    'Templates/Reports'
                ]
            },
            
            # Podcast Production
            {
                'name': 'Podcast Studio',
                'description': 'Podcast production workflow',
                'structure': [
                    'Episodes/Season 1/Raw Audio',
                    'Episodes/Season 1/Edited',
                    'Episodes/Season 1/Published',
                    'Episodes/Season 2/Raw Audio',
                    'Episodes/Season 2/Edited',
                    'Music/Intro',
                    'Music/Outro',
                    'Music/Background',
                    'SFX/Transitions',
                    'SFX/Bumpers',
                    'Show Notes/Drafts',
                    'Show Notes/Published',
                    'Guest/Interview Prep',
                    'Guest/Recordings',
                    'Guest/Releases',
                    'Scripts/Outlines',
                    'Scripts/Full Scripts',
                    'Marketing/Social Media',
                    'Marketing/Audiograms',
                    'Marketing/Graphics',
                    'Analytics/Downloads',
                    'Analytics/Demographics'
                ]
            },
            
            # E-commerce Store
            {
                'name': 'E-commerce Manager',
                'description': 'Online store organization',
                'structure': [
                    'Products/Active Listings',
                    'Products/Draft Listings',
                    'Products/Archived',
                    'Product Photos/Main',
                    'Product Photos/Detail',
                    'Product Photos/Lifestyle',
                    'Inventory/Stock Count',
                    'Inventory/Suppliers',
                    'Inventory/Orders',
                    'Orders/Pending/To Ship',
                    'Orders/Completed/2024',
                    'Orders/Completed/2025',
                    'Orders/Returns',
                    'Customers/Active',
                    'Customers/VIP',
                    'Marketing/Email Campaigns',
                    'Marketing/Promotions',
                    'Marketing/Social Media',
                    'Analytics/Sales Reports',
                    'Analytics/Traffic',
                    'Shipping/Labels',
                    'Shipping/Tracking'
                ]
            },
            
            # Real Estate Agent
            {
                'name': 'Real Estate Pro',
                'description': 'Real estate professional organization',
                'structure': [
                    'Listings/Active/Property 1',
                    'Listings/Active/Property 2',
                    'Listings/Sold/2024',
                    'Listings/Sold/2025',
                    'Properties/Photos/Exterior',
                    'Properties/Photos/Interior',
                    'Properties/Photos/Drone',
                    'Properties/Floor Plans',
                    'Properties/Virtual Tours',
                    'Clients/Buyers/Active',
                    'Clients/Buyers/Past',
                    'Clients/Sellers/Active',
                    'Clients/Sellers/Past',
                    'Contracts/Purchase Agreements',
                    'Contracts/Listing Agreements',
                    'Contracts/Disclosures',
                    'Marketing/Flyers',
                    'Marketing/Brochures',
                    'Marketing/Social Media',
                    'Open Houses/Scheduled',
                    'Open Houses/Completed',
                    'Market Research/Comps',
                    'Market Research/Trends'
                ]
            },
            
            # Recipe Collection
            {
                'name': 'Recipe Vault',
                'description': 'Recipe and meal planning',
                'structure': [
                    'Recipes/Breakfast',
                    'Recipes/Lunch',
                    'Recipes/Dinner',
                    'Recipes/Desserts',
                    'Recipes/Appetizers',
                    'Recipes/Beverages',
                    'Recipes/Favorites',
                    'Recipes/To Try',
                    'Meal Plans/Weekly',
                    'Meal Plans/Monthly',
                    'Meal Plans/Special Diet',
                    'Shopping Lists',
                    'Cooking Videos',
                    'Food Photos/Recipe Photos',
                    'Food Photos/Restaurant',
                    'Nutrition/Tracking',
                    'Nutrition/Meal Prep'
                ]
            }
        ]
    
    def get_all_templates(self) -> List[Dict]:
        """Get all available templates"""
        return self.templates
    
    def get_template_by_name(self, name: str) -> Dict:
        """Get a specific template by name"""
        for template in self.templates:
            if template['name'] == name:
                return template
        return None
    
    def apply_template(self, template: Dict, root_path: Path) -> bool:
        """Apply a template structure to a path"""
        try:
            for folder_path in template['structure']:
                full_path = root_path / folder_path
                full_path.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error applying template: {e}")
            return False
    
    def create_custom_template(self, name: str, description: str, 
                              structure: List[str]) -> Dict:
        """Create a custom template"""
        template = {
            'name': name,
            'description': description,
            'structure': structure
        }
        self.templates.append(template)
        return template