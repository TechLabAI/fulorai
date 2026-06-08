import { ComponentFixture, TestBed } from '@angular/core/testing';
import { WrksStylesComponent } from './wrks-styles.component';

describe('WrksStylesComponent', () => {
  let component: WrksStylesComponent;
  let fixture: ComponentFixture<WrksStylesComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [WrksStylesComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(WrksStylesComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
