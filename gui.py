import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import json
from all_speakers import AllSpeakers

class SpeakerAliasUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Speaker Alias Manager")
        self.root.geometry("800x600")
        
        self.speakers = AllSpeakers.all_speakers
        self.speaker_groups = {}  # Dictionary to store speaker groupings
        self.current_group_id = 1
        
        self.create_ui()
        # Call this method to populate the speakers list initially
        self.update_speaker_list()
    
    def create_ui(self):
        # Main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)
        
        # Top controls
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=5)
        
        ttk.Button(control_frame, text="Get Groupings", command=self.save_groupings).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Create Group", command=self.create_group).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Rename Selected Group", command=self.rename_group).pack(side=tk.LEFT, padx=5)
        ttk.Button(control_frame, text="Delete Selected Group", command=self.delete_group).pack(side=tk.LEFT, padx=5)
        
        # Left panel: Available speakers
        left_frame = ttk.LabelFrame(main_frame, text="Available Speakers")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a frame to hold the listbox and scrollbar
        list_frame = ttk.Frame(left_frame)
        list_frame.pack(fill=tk.BOTH, expand=True)
        
        self.speaker_listbox = tk.Listbox(list_frame, selectmode=tk.MULTIPLE)
        self.speaker_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Fix: Place scrollbar next to the listbox (not inside it)
        left_scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.speaker_listbox.yview)
        left_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.speaker_listbox.config(yscrollcommand=left_scrollbar.set)
        
        # Right panel: Speaker groups
        right_frame = ttk.LabelFrame(main_frame, text="Speaker Groups")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # Create a frame for the treeview and its scrollbar
        tree_frame = ttk.Frame(right_frame)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.groups_tree = ttk.Treeview(tree_frame)
        self.groups_tree["columns"] = ("aliases")
        self.groups_tree.column("#0", width=100, minwidth=100)
        self.groups_tree.column("aliases", width=300, minwidth=200)
        self.groups_tree.heading("#0", text="Group")
        self.groups_tree.heading("aliases", text="Aliases")
        self.groups_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # Add scrollbar for the treeview
        tree_scrollbar = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.groups_tree.yview)
        tree_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.groups_tree.config(yscrollcommand=tree_scrollbar.set)
        
        # Add right-click menu for group management
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(label="Rename Group", command=self.rename_group)
        self.context_menu.add_command(label="Delete Group", command=self.delete_group)
        
        self.groups_tree.bind("<Button-3>", self.show_context_menu)
        
        # Double-click to rename
        self.groups_tree.bind("<Double-1>", lambda event: self.rename_group())
        print(self.speakers)
        print(AllSpeakers.all_speakers)
    
    def update_speaker_list(self):
        self.speaker_listbox.delete(0, tk.END)
        
        # Get all speakers already in groups
        grouped_speakers = []
        for speakers in self.speaker_groups.values():
            grouped_speakers.extend(speakers)
        
        # Add speakers not in any group to the listbox
        for speaker in self.speakers:
            if speaker not in grouped_speakers:
                self.speaker_listbox.insert(tk.END, speaker)
    
    def create_group(self):
        selected_indices = self.speaker_listbox.curselection()
        
        if not selected_indices:
            messagebox.showwarning("Warning", "No speakers selected")
            return
            
        selected_speakers = [self.speaker_listbox.get(i) for i in selected_indices]
        
        # Ask for a group name instead of auto-generating one
        group_name = simpledialog.askstring("Create Group", "Enter a name for the new group:", 
                                           initialvalue=f"Group {self.current_group_id}")
        
        if not group_name:  # User cancelled
            return
            
        self.speaker_groups[group_name] = selected_speakers
        self.current_group_id += 1
        
        # Update tree view
        aliases_str = ", ".join(selected_speakers)
        self.groups_tree.insert("", "end", text=group_name, values=(aliases_str,))
        
        # Update available speakers
        self.update_speaker_list()
    
    def show_context_menu(self, event):
        item = self.groups_tree.identify_row(event.y)
        if item:
            self.groups_tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)
    
    def rename_group(self):
        selected = self.groups_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a group to rename")
            return
            
        item = selected[0]
        group_name = self.groups_tree.item(item, "text")
        
        new_name = simpledialog.askstring("Rename Group", "Enter new group name:", initialvalue=group_name)
        if new_name and new_name != group_name:
            # Check if the new name already exists
            if new_name in self.speaker_groups and new_name != group_name:
                messagebox.showerror("Error", f"A group named '{new_name}' already exists!")
                return
                
            # Update dictionary
            self.speaker_groups[new_name] = self.speaker_groups.pop(group_name)
            
            # Update tree
            aliases = self.groups_tree.item(item, "values")[0]
            self.groups_tree.item(item, text=new_name, values=(aliases,))
            
            messagebox.showinfo("Success", f"Group renamed from '{group_name}' to '{new_name}'")
    
    def delete_group(self):
        selected = self.groups_tree.selection()
        if not selected:
            messagebox.showinfo("Info", "Please select a group to delete")
            return
            
        item = selected[0]
        group_name = self.groups_tree.item(item, "text")
        
        if messagebox.askyesno("Confirm Delete", f"Are you sure you want to delete group '{group_name}'?"):
            # Remove from dictionary
            del self.speaker_groups[group_name]
            
            # Remove from tree
            self.groups_tree.delete(item)
            
            # Update available speakers
            self.update_speaker_list()
    
    def save_groupings(self):
        """Return the speaker groups dictionary"""
        if not self.speaker_groups:
            messagebox.showinfo("Information", "No groups defined yet")
            return {}
        
        # Display the dictionary to make it obvious it's being returned
        messagebox.showinfo("Speaker Groups", f"Speaker groups dictionary: {json.dumps(self.speaker_groups, indent=2)}")
        
        # Return the dictionary
        return self.speaker_groups
    
    def get_final_mapping(self):
        return self.speaker_groups