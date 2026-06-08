import { ComponentFixture, TestBed } from '@angular/core/testing';
import { LeadDataAccessComponent } from './lead-data-access.component';

describe('LeadDataAccessComponent', () => {
  let component: LeadDataAccessComponent;
  let fixture: ComponentFixture<LeadDataAccessComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [LeadDataAccessComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(LeadDataAccessComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
