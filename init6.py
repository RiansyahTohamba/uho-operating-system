"""
Educational Operating System Simulator
A simple OS implementation for teaching fundamental OS concepts
"""

import threading
import time
import queue
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional
import random


# ============================================================================
# WEEK 1-2: Process Management & Process States
# ============================================================================

class ProcessState(Enum):
    NEW = "NEW"
    READY = "READY"
    RUNNING = "RUNNING"
    WAITING = "WAITING"
    TERMINATED = "TERMINATED"


@dataclass
class Process:
    pid: int
    name: str
    priority: int
    burst_time: int
    arrival_time: int
    state: ProcessState
    waiting_time: int = 0
    turnaround_time: int = 0
    remaining_time: int = 0
    
    def __post_init__(self):
        self.remaining_time = self.burst_time


# ============================================================================
# WEEK 3: CPU Scheduling Algorithms
# ============================================================================

class Scheduler:
    def __init__(self):
        self.ready_queue = []
        self.current_process: Optional[Process] = None
        self.completed_processes = []
        self.time = 0
    
    def add_process(self, process: Process):
        """Add process to ready queue"""
        process.state = ProcessState.READY
        self.ready_queue.append(process)
        print(f"[Time {self.time}] Process {process.name} (PID: {process.pid}) added to ready queue")
    
    def fcfs_schedule(self):
        """First-Come-First-Served scheduling"""
        print("\n=== FCFS Scheduling ===")
        self.ready_queue.sort(key=lambda p: p.arrival_time)
        
        for process in self.ready_queue:
            process.state = ProcessState.RUNNING
            print(f"[Time {self.time}] Running {process.name} for {process.burst_time} units")
            
            process.waiting_time = self.time - process.arrival_time
            self.time += process.burst_time
            process.turnaround_time = self.time - process.arrival_time
            
            process.state = ProcessState.TERMINATED
            self.completed_processes.append(process)
        
        self.print_statistics()
    
    def sjf_schedule(self):
        """Shortest Job First scheduling"""
        print("\n=== SJF Scheduling ===")
        self.ready_queue.sort(key=lambda p: p.burst_time)
        
        for process in self.ready_queue:
            process.state = ProcessState.RUNNING
            print(f"[Time {self.time}] Running {process.name} (burst: {process.burst_time})")
            
            process.waiting_time = self.time - process.arrival_time
            self.time += process.burst_time
            process.turnaround_time = self.time - process.arrival_time
            
            process.state = ProcessState.TERMINATED
            self.completed_processes.append(process)
        
        self.print_statistics()
    
    def round_robin_schedule(self, time_quantum=2):
        """Round Robin scheduling with time quantum"""
        print(f"\n=== Round Robin Scheduling (Quantum: {time_quantum}) ===")
        queue_copy = self.ready_queue.copy()
        
        while queue_copy:
            process = queue_copy.pop(0)
            process.state = ProcessState.RUNNING
            
            exec_time = min(time_quantum, process.remaining_time)
            print(f"[Time {self.time}] Running {process.name} for {exec_time} units")
            
            self.time += exec_time
            process.remaining_time -= exec_time
            
            if process.remaining_time > 0:
                process.state = ProcessState.READY
                queue_copy.append(process)
            else:
                process.state = ProcessState.TERMINATED
                process.turnaround_time = self.time - process.arrival_time
                process.waiting_time = process.turnaround_time - process.burst_time
                self.completed_processes.append(process)
        
        self.print_statistics()
    
    def print_statistics(self):
        """Print scheduling statistics"""
        print("\n--- Scheduling Statistics ---")
        avg_waiting = sum(p.waiting_time for p in self.completed_processes) / len(self.completed_processes)
        avg_turnaround = sum(p.turnaround_time for p in self.completed_processes) / len(self.completed_processes)
        
        for p in self.completed_processes:
            print(f"{p.name}: Waiting={p.waiting_time}, Turnaround={p.turnaround_time}")
        
        print(f"\nAverage Waiting Time: {avg_waiting:.2f}")
        print(f"Average Turnaround Time: {avg_turnaround:.2f}")


# ============================================================================
# WEEK 4-5: Memory Management
# ============================================================================

class MemoryBlock:
    def __init__(self, start_addr: int, size: int, is_free: bool = True):
        self.start_addr = start_addr
        self.size = size
        self.is_free = is_free
        self.process_id: Optional[int] = None


class MemoryManager:
    def __init__(self, total_memory: int):
        self.total_memory = total_memory
        self.blocks = [MemoryBlock(0, total_memory)]
    
    def first_fit(self, process_id: int, size: int) -> bool:
        """First-fit memory allocation"""
        for block in self.blocks:
            if block.is_free and block.size >= size:
                if block.size > size:
                    # Split block
                    new_block = MemoryBlock(block.start_addr + size, block.size - size)
                    self.blocks.insert(self.blocks.index(block) + 1, new_block)
                
                block.size = size
                block.is_free = False
                block.process_id = process_id
                print(f"Allocated {size}KB to Process {process_id} at address {block.start_addr}")
                return True
        
        print(f"Failed to allocate {size}KB to Process {process_id}")
        return False
    
    def deallocate(self, process_id: int):
        """Free memory allocated to a process"""
        for block in self.blocks:
            if not block.is_free and block.process_id == process_id:
                block.is_free = True
                block.process_id = None
                print(f"Deallocated memory for Process {process_id}")
                self.coalesce()
                return True
        return False
    
    def coalesce(self):
        """Merge adjacent free blocks"""
        i = 0
        while i < len(self.blocks) - 1:
            if self.blocks[i].is_free and self.blocks[i + 1].is_free:
                self.blocks[i].size += self.blocks[i + 1].size
                self.blocks.pop(i + 1)
            else:
                i += 1
    
    def display_memory(self):
        """Display memory layout"""
        print("\n--- Memory Layout ---")
        for block in self.blocks:
            status = "FREE" if block.is_free else f"P{block.process_id}"
            print(f"[{block.start_addr:4d}-{block.start_addr + block.size:4d}] {block.size:4d}KB {status}")


# ============================================================================
# WEEK 6: Paging System
# ============================================================================

class PageTable:
    def __init__(self, page_size: int = 4):
        self.page_size = page_size
        self.table = {}  # page_number -> frame_number
    
    def add_mapping(self, page_num: int, frame_num: int):
        self.table[page_num] = frame_num
    
    def translate(self, logical_addr: int) -> Optional[int]:
        """Translate logical address to physical address"""
        page_num = logical_addr // self.page_size
        offset = logical_addr % self.page_size
        
        if page_num in self.table:
            frame_num = self.table[page_num]
            physical_addr = frame_num * self.page_size + offset
            print(f"Logical {logical_addr} -> Page {page_num}, Offset {offset} -> Frame {frame_num} -> Physical {physical_addr}")
            return physical_addr
        else:
            print(f"Page fault! Page {page_num} not in memory")
            return None


# ============================================================================
# WEEK 7: Synchronization - Semaphores
# ============================================================================

class Semaphore:
    def __init__(self, initial_value: int = 1):
        self.value = initial_value
        self.lock = threading.Lock()
        self.waiting_queue = []
    
    def wait(self, process_name: str):
        """P operation (wait/down)"""
        with self.lock:
            self.value -= 1
            if self.value < 0:
                print(f"{process_name} is waiting...")
                self.waiting_queue.append(process_name)
                return False
            print(f"{process_name} acquired semaphore")
            return True
    
    def signal(self, process_name: str):
        """V operation (signal/up)"""
        with self.lock:
            self.value += 1
            print(f"{process_name} released semaphore")
            if self.waiting_queue:
                woken = self.waiting_queue.pop(0)
                print(f"{woken} woken up")


# ============================================================================
# WEEK 8: Deadlock Detection
# ============================================================================

class DeadlockDetector:
    def __init__(self, num_processes: int, num_resources: int):
        self.allocation = [[0] * num_resources for _ in range(num_processes)]
        self.max_need = [[0] * num_resources for _ in range(num_processes)]
        self.available = [0] * num_resources
        self.num_processes = num_processes
        self.num_resources = num_resources
    
    def set_allocation(self, process: int, resources: List[int]):
        self.allocation[process] = resources.copy()
    
    def set_max_need(self, process: int, resources: List[int]):
        self.max_need[process] = resources.copy()
    
    def set_available(self, resources: List[int]):
        self.available = resources.copy()
    
    def detect_deadlock(self) -> bool:
        """Banker's algorithm for deadlock detection"""
        work = self.available.copy()
        finish = [False] * self.num_processes
        need = [[self.max_need[i][j] - self.allocation[i][j] 
                 for j in range(self.num_resources)] 
                for i in range(self.num_processes)]
        
        safe_sequence = []
        
        while len(safe_sequence) < self.num_processes:
            found = False
            for i in range(self.num_processes):
                if not finish[i] and all(need[i][j] <= work[j] for j in range(self.num_resources)):
                    work = [work[j] + self.allocation[i][j] for j in range(self.num_resources)]
                    finish[i] = True
                    safe_sequence.append(i)
                    found = True
                    break
            
            if not found:
                print("System is in DEADLOCK state!")
                print(f"Deadlocked processes: {[i for i, f in enumerate(finish) if not f]}")
                return True
        
        print("System is in SAFE state!")
        print(f"Safe sequence: {safe_sequence}")
        return False


# ============================================================================
# WEEK 9: File System Simulation
# ============================================================================

class INode:
    def __init__(self, inode_id: int, name: str, is_directory: bool = False):
        self.inode_id = inode_id
        self.name = name
        self.is_directory = is_directory
        self.size = 0
        self.content = "" if not is_directory else {}
        self.created_time = time.time()


class FileSystem:
    def __init__(self):
        self.root = INode(0, "/", is_directory=True)
        self.current_dir = self.root
        self.inode_counter = 1
    
    def create_file(self, name: str, content: str = ""):
        """Create a new file in current directory"""
        if name in self.current_dir.content:
            print(f"File '{name}' already exists!")
            return False
        
        new_file = INode(self.inode_counter, name)
        new_file.content = content
        new_file.size = len(content)
        self.current_dir.content[name] = new_file
        self.inode_counter += 1
        print(f"Created file '{name}' (inode: {new_file.inode_id})")
        return True
    
    def create_directory(self, name: str):
        """Create a new directory"""
        if name in self.current_dir.content:
            print(f"Directory '{name}' already exists!")
            return False
        
        new_dir = INode(self.inode_counter, name, is_directory=True)
        self.current_dir.content[name] = new_dir
        self.inode_counter += 1
        print(f"Created directory '{name}'")
        return True
    
    def list_directory(self):
        """List contents of current directory"""
        print(f"\nContents of {self.current_dir.name}:")
        for name, inode in self.current_dir.content.items():
            file_type = "DIR" if inode.is_directory else "FILE"
            print(f"  [{file_type}] {name} (size: {inode.size} bytes)")
    
    def read_file(self, name: str):
        """Read file content"""
        if name not in self.current_dir.content:
            print(f"File '{name}' not found!")
            return None
        
        inode = self.current_dir.content[name]
        if inode.is_directory:
            print(f"'{name}' is a directory!")
            return None
        
        print(f"Content of '{name}':")
        print(inode.content)
        return inode.content


# ============================================================================
# WEEK 10: I/O Management & Disk Scheduling
# ============================================================================

class DiskScheduler:
    def __init__(self, total_cylinders: int = 200):
        self.total_cylinders = total_cylinders
    
    def fcfs_disk(self, requests: List[int], head_start: int):
        """FCFS disk scheduling"""
        print(f"\n=== FCFS Disk Scheduling ===")
        print(f"Initial head position: {head_start}")
        
        total_seek = 0
        current = head_start
        
        for req in requests:
            seek = abs(req - current)
            total_seek += seek
            print(f"Move from {current} to {req} (seek: {seek})")
            current = req
        
        print(f"Total seek time: {total_seek}")
        return total_seek
    
    def scan_disk(self, requests: List[int], head_start: int, direction: str = "right"):
        """SCAN (elevator) disk scheduling"""
        print(f"\n=== SCAN Disk Scheduling ===")
        print(f"Initial head position: {head_start}, Direction: {direction}")
        
        left = [r for r in requests if r < head_start]
        right = [r for r in requests if r >= head_start]
        
        left.sort()
        right.sort()
        
        total_seek = 0
        current = head_start
        
        if direction == "right":
            sequence = right + [self.total_cylinders - 1] + left[::-1]
        else:
            sequence = left[::-1] + [0] + right
        
        for req in sequence:
            seek = abs(req - current)
            total_seek += seek
            print(f"Move from {current} to {req} (seek: {seek})")
            current = req
        
        print(f"Total seek time: {total_seek}")
        return total_seek


# ============================================================================
# DEMONSTRATION & TESTING
# ============================================================================

def demo_week_1_2():
    """Demo: Process Management"""
    print("\n" + "="*60)
    print("WEEK 1-2: Process Management & States")
    print("="*60)
    
    p1 = Process(1, "Editor", 2, 5, 0, ProcessState.NEW)
    p2 = Process(2, "Compiler", 1, 8, 2, ProcessState.NEW)
    
    print(f"Created Process: {p1.name} (PID: {p1.pid}, Priority: {p1.priority})")
    print(f"Created Process: {p2.name} (PID: {p2.pid}, Priority: {p2.priority})")
    print(f"\nProcess states: {[state.value for state in ProcessState]}")


def demo_week_3():
    """Demo: CPU Scheduling"""
    print("\n" + "="*60)
    print("WEEK 3: CPU Scheduling Algorithms")
    print("="*60)
    
    scheduler = Scheduler()
    processes = [
        Process(1, "P1", 1, 5, 0, ProcessState.NEW),
        Process(2, "P2", 2, 3, 1, ProcessState.NEW),
        Process(3, "P3", 1, 8, 2, ProcessState.NEW),
    ]
    
    for p in processes:
        scheduler.add_process(p)
    
    scheduler.fcfs_schedule()


def demo_week_4_5():
    """Demo: Memory Management"""
    print("\n" + "="*60)
    print("WEEK 4-5: Memory Management")
    print("="*60)
    
    mem_mgr = MemoryManager(100)
    mem_mgr.first_fit(1, 20)
    mem_mgr.first_fit(2, 30)
    mem_mgr.first_fit(3, 15)
    mem_mgr.display_memory()
    
    mem_mgr.deallocate(2)
    mem_mgr.display_memory()


def demo_week_6():
    """Demo: Paging"""
    print("\n" + "="*60)
    print("WEEK 6: Paging System")
    print("="*60)
    
    page_table = PageTable(page_size=4)
    page_table.add_mapping(0, 2)
    page_table.add_mapping(1, 5)
    page_table.add_mapping(2, 1)
    
    page_table.translate(0)
    page_table.translate(7)
    page_table.translate(10)


def demo_week_7():
    """Demo: Synchronization"""
    print("\n" + "="*60)
    print("WEEK 7: Synchronization - Semaphores")
    print("="*60)
    
    sem = Semaphore(initial_value=1)
    sem.wait("Process A")
    sem.wait("Process B")
    sem.signal("Process A")


def demo_week_8():
    """Demo: Deadlock Detection"""
    print("\n" + "="*60)
    print("WEEK 8: Deadlock Detection")
    print("="*60)
    
    detector = DeadlockDetector(3, 3)
    detector.set_allocation(0, [0, 1, 0])
    detector.set_allocation(1, [2, 0, 0])
    detector.set_allocation(2, [3, 0, 2])
    
    detector.set_max_need(0, [7, 5, 3])
    detector.set_max_need(1, [3, 2, 2])
    detector.set_max_need(2, [9, 0, 2])
    
    detector.set_available([3, 3, 2])
    detector.detect_deadlock()


def demo_week_9():
    """Demo: File System"""
    print("\n" + "="*60)
    print("WEEK 9: File System Simulation")
    print("="*60)
    
    fs = FileSystem()
    fs.create_file("hello.txt", "Hello, World!")
    fs.create_file("readme.md", "# Operating System Project")
    fs.create_directory("documents")
    fs.list_directory()
    fs.read_file("hello.txt")


def demo_week_10():
    """Demo: Disk Scheduling"""
    print("\n" + "="*60)
    print("WEEK 10: I/O Management & Disk Scheduling")
    print("="*60)
    
    scheduler = DiskScheduler(200)
    requests = [98, 183, 37, 122, 14, 124, 65, 67]
    
    scheduler.fcfs_disk(requests, 53)
    scheduler.scan_disk(requests, 53, "right")


if __name__ == "__main__":
    print("\n" + "="*60)
    print("EDUCATIONAL OPERATING SYSTEM SIMULATOR")
    print("="*60)
    
    demo_week_1_2()
    demo_week_3()
    demo_week_4_5()
    demo_week_6()
    demo_week_7()
    demo_week_8()
    demo_week_9()
    demo_week_10()
    
    print("\n" + "="*60)
    print("All demonstrations completed!")
    print("="*60)