// ── User ──
export interface User {
	id: string;
	email: string;
	username: string;
	firstName: string;
	lastName: string;
	emailVerified: boolean;
	profileImage: string | null;
	dateJoined: string;
}

// ── Organization ──
export type OrgRole = 'OWNER' | 'ADMIN' | 'MEMBER';

export interface OrganizationMembership {
	id: string;
	role: OrgRole;
	joinedAt: string;
	user: Pick<User, 'id' | 'email' | 'username' | 'firstName' | 'lastName' | 'profileImage'>;
}

export interface Organization {
	id: string;
	name: string;
	slug: string;
	description: string;
	createdBy: Pick<User, 'id' | 'email'>;
	createdAt: string;
	updatedAt: string;
	members: OrganizationMembership[];
}

// ── Project ──
export interface ProjectMembership {
	id: string;
	joinedAt: string;
	user: Pick<User, 'id' | 'email' | 'username' | 'firstName' | 'lastName' | 'profileImage'>;
	addedBy: Pick<User, 'id' | 'email'>;
}

export interface Project {
	id: string;
	name: string;
	slug: string;
	description: string;
	organization: Pick<Organization, 'id' | 'name'>;
	createdBy: Pick<User, 'id' | 'email'>;
	createdAt: string;
	updatedAt: string;
	members: ProjectMembership[];
}

// ── Board ──
export interface Board {
	id: string;
	name: string;
	slug: string;
	description: string;
	project: Pick<Project, 'id' | 'name'>;
	createdBy: Pick<User, 'id' | 'email'>;
	createdAt: string;
	updatedAt: string;
	taskGroups: TaskGroup[];
}

// ── TaskGroup ──
export interface TaskGroup {
	id: string;
	name: string;
	position: number;
	createdAt: string;
	updatedAt: string;
	tasks: Task[];
}

// ── Task ──
export type TaskStatus = 'TODO' | 'IN_PROGRESS' | 'IN_REVIEW' | 'DONE';
export type TaskPriority = 'LOW' | 'MEDIUM' | 'HIGH' | 'URGENT';

export interface Task {
	id: string;
	title: string;
	description: string;
	status: TaskStatus;
	priority: TaskPriority;
	position: number;
	taskGroup: Pick<TaskGroup, 'id' | 'name'>;
	assignee: Pick<User, 'id' | 'email' | 'username' | 'firstName' | 'lastName' | 'profileImage'> | null;
	dueDate: string | null;
	labels: Label[];
	createdBy: Pick<User, 'id' | 'email'>;
	commentCount: number;
	createdAt: string;
	updatedAt: string;
}

// ── Label ──
export interface Label {
	id: string;
	name: string;
	color: string;
}

// ── Pagination ──
export interface PaginationInput {
	limit: number;
	offset: number;
}

export interface PaginatedResult<T> {
	totalCount: number;
	hasNext: boolean;
	hasPrevious: boolean;
	items: T[];
}

// ── Task Filter ──
export interface TaskFilterInput {
	status?: TaskStatus[];
	priority?: TaskPriority[];
	assigneeId?: string;
	dueDateFrom?: string;
	dueDateTo?: string;
	search?: string;
	labelIds?: string[];
}

// ── Auth ──
export interface LoginResponse {
	access: string;
	refresh: string;
	user: {
		id: number;
		email: string;
		username: string;
		first_name: string;
		last_name: string;
	};
}

export interface TokenRefreshResponse {
	access: string;
	refresh: string;
}
